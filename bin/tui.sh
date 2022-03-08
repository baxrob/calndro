#!/bin/sh

DEFAULT_USER=ob
DEFAULT_PASS=p

user=${user:-$DEFAULT_USER}
pass=${pass:-$DEFAULT_PASS}
host=${host:-}
port=${port:-8000}


echo ${user:-_} ${pass:-_} ${host:-_} ${port-_}

prompt() {
    #echo m $1
    case $1 in
    menu) printf "    l  d[n]  c[n]  p[n]  n[n]  g[n]  ?  \n> " ;;

    create_parties) printf "create: enter party emails>\n" ;;
    create_slots)
    printf "create: enter slots as YYYY-MM-DDThh:mm:ss[+-mm:ss/Z] hh:mm:ss>\n"
    ;;
    create_slots_nop) ;;

    patch)
    p=$(req detail $2 | jq .parties)
    np=$(nlist "$p")
    printf "$p\n"
    printf "patch: enter slots by number> "
    ;;
    patch_nop) ;;
    
    notify)
    p=$(http --print=b -a $user:$pass $host:$port/$2/ | jq .parties)
    printf "$p\n"
    printf "notify: enter parties by number> "
    ;;
    
    *) printf "    [nop $1 $2\n]" ;;
    esac
}

sess() {
    :
}

req() {
    case $1 in
    list) 
    http --print=b -a $user:$pass $host:$port/
    ;;
    detail)
    http --print=b -a $user:$pass $host:$port/$2/
    ;;
    log)
    http --print=b -a $user:$pass $host:$port/$2/log/
    ;;
    create) ;;
    patch) ;;
    notify) ;;
    esac
}

create() {
    printf "p: $1\n"
    printf "s:\n$2\n"
}

nlist() {
    :
}

listn() {
    :
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
        '?') printf "l list\nd detail\np patch\nn notify\ng log\n? help\n" ;;
        # X:
        *) echo huh? $cmd ;; #pcode=menu ;;
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
    patch|patch_nop)
    s=$(nlist "$cmd" $(req detail $evtnum | jq .slots))
    req patch $evtnum "$s"
    pcode=menu
    ;;
    notify)
    p=$(nlist "$cmd" $(req detail $evtnum | jq .parties))
    s=$(req detail $2 | jq .slots)
    req notify "$p" "$s"
    pcode=menu
    ;;

    *) echo whot? $cmd ;;
    esac
    prompt $pcode $evtnum
done


exit

#while cmd=$(menu $prompt); do
while true; do
    :
    break
done

while read CMD; do
    #echo $CMD
    break
done

while $(read CMD); do
    #echo $CMD
    break
done


