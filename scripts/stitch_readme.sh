#!/bin/sh

quiet=$([ "$1" != "-q" ]; echo $?)

thispath="$(dirname "$0")"
basepath="$thispath/.."
partspath="${partspath:-"$thispath/../_README"}"
mapfilename=${mapfilename:-map}
mappath="$partspath/$mapfilename"
outpath=${outpath:-"$thispath/../README.md"}

echo outpath $outpath

[ $quiet -ne 0 ] || echo config: $thispath $basepath $partspath \
    $mapfilename $mappath $outpath

# X: grip
# N: ttscoff/mdless
pager=$(which mdless > /dev/null && printf %s 'mdless --no-color' || which less || which more)

subs() {
    cd "$basepath"
    case $1 in
    cloc)
    cl=$(cloc --vcs=git) # "$(realpath "$basepath")")
    clc=$(printf "$cl" | wc -l)
    #echo $clc $basepath
    # X: '5' 
    clp=$(printf "$cl" | tail -n $(($clc - 5)))
    #printf "%s\n%s\n" "$clp" "[cloc](/AlDanial/cloc)"
    printf "%s\n" "$clp"
    ;;
    wc)
    find schedul -name '*.py' -exec wc -l {} \; | grep -v migrations \
        | awk '{ 
            OFS = "\t"
            print $1, $2 
        }' | sort -hr
    ;;
    coverage) 
    which coverage > /dev/null && coverage report || echo '%[nocoverage]'
    ;;
    tuisrc) cat scripts/tui.sh ;;
    tree)
    ex="venv|_README|__pycache__|_a|_t|_aux|migrations|fixtures|\
        requirements|openapi-fuzzer|lib|coverage|tests|_m|LICENSE|\
        gpl-3.0.txt|db.sqlite3|README.md|*.vim|readme_draft.md"
    #echo '   bo  lo fro  ' | sed 's/\b /|/g; s/ //g; s/|$//'
    ex="$(echo "$ex" | sed 's/ //g')"
    # X:
    #tree -n -I "venv|_README|__pycache__|_a|_t|_aux|migrations|fixtures|requirements|openapi-fuzzer|lib|coverage|tests|_m|LICENSE|gpl-3.0.txt|db.sqlite3|README.md|*.vim" | sed '$d'
    tree -n -I "$ex" | sed \$d
    #ig="$ig|..." 
    #out="$(tree -n -I "$ig") 
    #tn=$(($(printf "$out" | wc -l) - 2)) 
    #printf "$out" | sed $tn\$d
    ##printf "$out" | head -n $tn
    ;;
    annotree) echo "%[..$1]"
    subs = "
       Dockerfile-alp-pg
       Dockerfile-pg
       ngx
       config
       schedul
       init_pg.sh
       reset.sh
    "
    ;;
    testdo)
    # X:
    checks="$(grep -n -B 1 todo- schedul/tests.py | grep test_ \
        | sed 's/^.*\(test_.*\)(.*/\1/')"
    [ -n "$checks" ] && printf "verify:\n%s\n" "$checks"
    writes="$(grep -n -B 1 todo$ schedul/tests.py | grep test_ \
        | sed 's/^.*\(test_.*\)(.*/\1/')"
    [ -n "$writes" ] && printf "\nfinish:\n%s\n" "$writes"
    ;;
    *) echo "%[??$1]" ;;
    esac
    cd - > /dev/null
}


doc=$(for file in $(cat $mappath); do
    fdoc=$(cat "$partspath/${file}.md")
    mlines=$(echo "$fdoc" | grep -n '%\[')
    #echo '==  '$file m 
    if [ -n "$mlines" ]; then
        # X: echo ..\n re limit<offset below
        doclen=$(echo "$fdoc" | wc -l)
        mcount=$(echo "$mlines" | wc -l)

        #doclen=$(printf "%s" "$fdoc" | wc -l)
        #mcount=$(printf "%s" "$mlines" | wc -l)
        idx=1
        offset=1
        for line in $mlines; do

            n=$(echo $line | awk -F: '{ print $1 }')
            term=$(echo $line | awk -F: '{ print $2 }' \
                | sed 's/%\[\(.*\)\]/\1/')
            
            # X: 
            limit=$(($n - 1))

            #limit=$(($n - 0))
            #echo '==  't $term $doclen $n $idx $mcount $offset $limit

            if [ $limit -ge $offset ]; then
                # X: p=q
                printf %s "$fdoc" \
                    | sed -n $offset','$limit'p;'$(($limit + 1))'q'
            fi

            #echo "===$term==="
            subs $term

            if [ $idx -eq $mcount ]; then
                printf "%s\n" "$fdoc" \
                    | sed -n $(($limit + 2))','$(($doclen))'p'
            fi
            idx=$(($idx + 1))
            offset=$(($n + 1))
        done
    else
        printf "%s\n" "$fdoc"
    fi
done)

if [ $quiet -eq 0 ]; then
#echo "$doc" | mdless
    echo "$doc" | eval "$pager"

    echo Enter to write to $outpath or ctrl-c to quit

    read foo
fi

dt=$(date +%Y%m%d-%H%M%S)

#echo $outpath  
echo "$doc" > $outpath && { echo written $dt; ls -lh $outpath; }



# X:
dir=${1:-../_README}
segmap=$dir/map
verdir=$dir/ver
target=${2:-$verdir/README_$dt.md}

#echo "$doc" > GARBAGE-rdmd_$dt
#diff $tmpname $file

