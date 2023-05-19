#!/bin/sh

host=${host:-}
port=${port:-} 
#sender=${sender:-}
print=${print:-b}

user=${user:-}
pass=${pass-} # declare as empty to prompt
session=${session:-}
token=${token:-}

auth=
if [ -n "$token" ]; then
    auth="-a $token"
elif [ -n "$user" ]; then
    while [ -z "$pass" ]; do
        echo -n 'Password: '
        pass=$(bash -c 'read -s x; echo $x')
        echo
        [ -z "$pass" ] && echo got blank
    done
    auth="-a $user:$pass"
fi
if [ -n "$session" ]; then
    auth="$auth --session=$session"
fi

showauth=$(echo $auth | sed 's/:[^ ]*/:***/')
printf "config:\n  auth: $showauth\n  addr: $host:$port\n  print: $print\n"

which jq > /dev/null || { echo jq required; exit 1; }

prompt() {
    case $1 in
    menu) printf "  l   c   d[n]  p[n]  n[n]  g[n]  ?   q\n> " ;;

    create_title) printf "create: enter event tile or blank to generate>\n" ;;
    create_parties) printf "enter party emails>\n" ;;
    create_slots)
    printf "enter slots as YYYY-MM-DDThh:mm:ss[+-hh:mm/Z] hh:mm:ss"
    printf ", followed by blank>\n"
    ;;
    create_slots_nop) ;;

    patch)
    s=$(req detail $2 | jq .slots)
    nlist "$s"
    printf "patch: enter slots by number> "
    ;;
    
    notify_*)
    echo prompt notify ${1#*_}
    p=$(req detail $2 | jq .parties)
    nlist "$p"
    if [ ${1#*_} = parties ]; then
        printf "notify: enter parties by number> "
    elif [ ${1#*_} = sender ]; then
        printf "enter sender by number or blank for [1]> "
    fi
    ;;
    
    *) printf "  [nop $1 $2\n]" ;;
    esac
}

req() {
    #echo req $@
    case $1 in
    #list) http --print=b -a $user:$pass $host:$port/ ;;
    #detail) http --print=b -a $user:$pass $host:$port/$2/ ;;
    #log) http --print=b -a $user:$pass $host:$port/$2/log/ ;;
    list) http --print=$print $auth $host:$port/ ;;
    detail) http --print=$print $auth $host:$port/$2/ ;;
    log) http --print=$print $auth $host:$port/$2/log/ ;;
    create)
    #titledecl=$([ -n "$4" ] && printf title="$4" || printf "")
    #echo $titledecl
    hcmd="http --print=$print $auth $host:$port/ parties:="$2" slots:="$3""
    #hcmd="http --print=b -a $user:$pass $host:$port/ parties:="$2" slots:="$3""
    if [ -n "$4" ]; then
        hcmd="$hcmd title="$4""
    fi
    echo $($hcmd)
    #http --print=b -a $user:$pass $host:$port/ parties:="$2" \
    #    slots:="$3" "$titledecl"
       # title="$4"
    ;;
    #patch) http --print=b -a $user:$pass PATCH $host:$port/$2/ slots:="$3" ;;
    patch) http --print=$print $auth PATCH $host:$port/$2/ slots:="$3" ;;
    notify)
    #echo $@
    #echo http --print=b -a $user:$pass POST $host:$port/$2/notify/ \
    #    parties:="$3" slots:="$4" sender=$5
    #http --print=b -a $user:$pass POST $host:$port/$2/notify/ \
    #    parties:="$3" slots:="$4" sender=$5
    echo http --print=$print $auth POST $host:$port/$2/notify/ \
        parties:="$3" slots:="$4" sender=$5
    http --print=$print $auth POST $host:$port/$2/notify/ \
        parties:="$3" slots:="$4" sender=$5
    ;;
    esac
}

create() {
    plist='[' # quoted for vim syntax highlighting
    for eml in $1; do
        plist="$plist\"$eml\","
    done
    plist=$(echo $plist | sed 's/,*$/]/')
    slist='['
    slist=$slist$(echo $2 | awk '/./ {
        printf("{\"begin\": \"%s\", \"duration\": \"%s\"},", $1, $2)
    }')
    slist=$(echo $slist | sed 's/,*$/]/')
    req create "$plist" "$slist" "$3"
}

nlist() {
    len=$(echo "$1" | jq 'length')
    for i in $(seq $len); do
        echo $i $(echo "$1" | jq '.['$(($i - 1))']')
    done
}

listn() {
    list='['
    for i in $1; do
        list="$list$(($i - 1)),"
    done
    list=$(echo $list | sed 's/,*$/]/')
    echo $2 | jq -cM [.$list]
}

evtnum=
cparties=
cslots=

nparties=
#nsender=


## Run loop ##

pcode=menu

prompt $pcode

# X: posix but no readline 
#while read cmd; do
while cmd=$(bash -c 'read -er cmd; echo $cmd'); do
    case $pcode in
    menu)
        case "$cmd" in
        l) req list ;;
        c) pcode=create_title ;;
        d[0-9]*) req detail ${cmd#d} ;;
        p[0-9]*) evtnum=${cmd#p}; pcode=patch ;;
        #n[0-9]*) evtnum=${cmd#n}; pcode=notify ;;
        n[0-9]*) evtnum=${cmd#n}; pcode=notify_parties ;;
        g[0-9]*) req log ${cmd#g} ;;
        '?')
        printf "l list events\n"
        printf "c create - prompts for emails, time-spans\n"
        printf "d[n] detail - view event number n\n"
        printf "p[n] patch time-spans for event n\n"
        printf "n[n] notify recipients for n\n"
        #printf "n[n] notify recipients for n - prompts for sender\n"
        printf "g[n] log - view dispatch/update logs\n"
        printf "? help - this help\n"
        printf "q quit\n"
        ;;
        q) exit 0 ;;
        # X:
        *) printf "\nhuh? $cmd\n" ;; #pcode=menu ;;
        esac
    ;;
    create_title) ctitle="$cmd"; pcode=create_parties ;;
    create_parties) cparties="$cmd"; pcode=create_slots ;;
    create_slots|create_slots_nop)
    if [ -n "$cmd" ]; then
        cslots="${cslots#\\n}\n$cmd"
        pcode=create_slots_nop
    else
        create "$cparties" "$cslots" "$ctitle"
        cslots=
        pcode=menu
    fi
    ;;
    patch)
    #listn "$cmd" "$(req detail $evtnum | jq .slots)"
    s=$(listn "$cmd" "$(req detail $evtnum | jq -c .slots)")
    #printf "ps $s\n"
    #s=$cmd
    req patch $evtnum "$s"
    pcode=menu
    ;;
    notify)
    parties=$(listn "$cmd" "$(req detail $evtnum | jq -c .parties)")
    slots=$(req detail $evtnum | jq -c .slots)
    req notify $evtnum "$parties" "$slots"
    pcode=menu
    ;;
    notify_*)
    if [ ${pcode#*_} = parties ]; then
        nparties=$(listn "$cmd" "$(req detail $evtnum | jq -c .parties)")
        pcode=notify_sender
    elif [ ${pcode#*_} = sender ]; then
        cmd=$([ -z "$cmd" ] && echo 1 || echo "$cmd")
        sender=$(listn "$cmd" "$(req detail $evtnum | jq -c .parties)" \
            | jq .[0] | sed 's/"//g')
        echo Sender $sender
        slots=$(req detail $evtnum | jq .slots)
        req notify $evtnum "$nparties" "$slots" $sender
        pcode=menu
    fi
    ;;

    *) echo [whot? $cmd] ;;
    esac
    prompt $pcode $evtnum
done

