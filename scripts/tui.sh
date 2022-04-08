#!/bin/sh

DEFAULT_USER=ob
DEFAULT_PASS=p
DEFAULT_SENDER=ob@localhost

user=${user:-$DEFAULT_USER}
pass=${pass:-$DEFAULT_PASS}
host=${host:-}
port=${port:-8000}
sender=${sender:-$DEFAULT_SENDER}

echo config: ${user:-_} ${pass:-_} ${host:-_} ${port:-_} $sender

prompt() {
    case $1 in
    menu) printf "  l   c   d[n]  p[n]  n[n]  g[n]  ?   q\n> " ;;

    create_parties) printf "create: enter party emails>\n" ;;
    create_slots)
    printf "enter slots as YYYY-MM-DDThh:mm:ss[+-mm:ss/Z] hh:mm:ss"
    printf ", followed by blank>\n"
    ;;
    create_slots_nop) ;;

    patch)
    s=$(req detail $2 | jq .slots)
    nlist "$s"
    printf "patch: enter slots by number> "
    ;;
    
    notify)
    p=$(req detail $2 | jq .parties)
    nlist "$p"
    printf "notify: enter parties by number> "
    ;;
    
    *) printf "  [nop $1 $2\n]" ;;
    esac
}

sess() {
    :
}

req() {
    case $1 in
    list) http --print=b -a $user:$pass $host:$port/ ;;
    detail) http --print=b -a $user:$pass $host:$port/$2/ ;;
    log) http --print=b -a $user:$pass $host:$port/$2/log/ ;;
    create)
    http --print=b -a $user:$pass $host:$port/ parties:="$2" slots:="$3"
    ;;
    patch) http --print=b -a $user:$pass PATCH $host:$port/$2/ slots:="$3" ;;
    notify)
    http --print=b -a $user:$pass $host:$port/$2/notify \
        parties:="$3" slots:="$4"
    ;;
    esac
}

create() {
    plist=[
    for eml in $1; do
        plist="$plist\"$eml\","
    done
    plist=$(echo $plist | sed 's/,*$/]/')
    slist=[
    slist=$slist$(echo $2 | awk '/./ {
        printf("{\"begin\": \"%s\", \"duration\": \"%s\"},", $1, $2)
    }')
    slist=$(echo $slist | sed 's/,*$/]/')
    req create "$plist" "$slist"
}

nlist() {
    len=$(echo "$1" | jq 'length')
    for i in $(seq $len); do
        echo $i $(echo "$1" | jq '.['$(($i - 1))']')
    done
}

listn() {
    list=[
    for i in $1; do
        list="$list$(($i - 1)),"
    done
    list=$(echo $list | sed 's/,*$/]/')
    echo $2 | jq -cM [.$list]
}

evtnum=
cparties=
cslots=

pcode=menu

prompt $pcode

#while read cmd; do
while cmd=$(bash -c 'read -er cmd; echo $cmd'); do
    case $pcode in
    menu)
        case "$cmd" in
        l) req list ;;
        c) pcode=create_parties ;;
        d[0-9]*) req detail ${cmd#d} ;;
        p[0-9]*) evtnum=${cmd#p}; pcode=patch ;;
        n[0-9]*) evtnum=${cmd#n}; pcode=notify ;;
        g[0-9]*) req log ${cmd#g} ;;
        '?')
        printf "l list events\n"
        printf "c create - prompst for emails, time-spans\n"
        printf "d[n] detail - view event number n\n"
        printf "p[n] patch time-spans for event n\n"
        printf "n[n] notify recipients for n\n"
        printf "g[n] log - view dispatch/update logs\n"
        printf "? help - this help\n"
        printf "q quit\n"
        ;;
        q) exit 0 ;;
        # X:
        *) printf "\nhuh? $cmd\n" ;; #pcode=menu ;;
        esac
    ;;
    create_parties) cparties="$cmd"; pcode=create_slots ;;
    create_slots|create_slots_nop)
    if [ -n "$cmd" ]; then
        cslots="${cslots#\\n}\n$cmd"
        pcode=create_slots_nop
    else
        create "$cparties" "$cslots"
        pcode=menu
    fi
    ;;
    patch)
    #listn "$cmd" "$(req detail $evtnum | jq .slots)"
    s=$(listn "$cmd" "$(req detail $evtnum | jq .slots)")
    #printf "ps $s\n"
    #s=$cmd
    req patch $evtnum "$s"
    pcode=menu
    ;;
    notify)
    p=$(listn "$cmd" "$(req detail $evtnum | jq .parties)")
    #p="$cmd"
    s=$(req detail $evtnum | jq .slots)
    req notify $evtnum "$p" "$s"
    pcode=menu
    ;;

    *) echo [whot? $cmd] ;;
    esac
    prompt $pcode $evtnum
done

