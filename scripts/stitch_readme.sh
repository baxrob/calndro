#!/bin/sh

quiet=$([ "$1" != "-q" ]; echo $?)

thispath="$(dirname "$0")"
basepath="$thispath/.."
partspath="${partspath:-"$thispath/../_README"}"
mapfilename=${mapfilename:-map}
mappath="$partspath/$mapfilename"
outpath=${outpath:-"$thispath/../README.md"}

[ $quiet -ne 0 ] || echo config: $thispath $basepath $partspath \
    $mapfilename $mappath $outpath

# X: grip
# N: ttscoff/mdless
pager=$(which mdless || which less || which more)

subs() {
    cd "$basepath"
    case $1 in
    cloc)
    cl=$(cloc --vcs=git) # "$(realpath "$basepath")")
    clc=$(printf "$cl" | wc -l)
    #echo $clc $basepath
    
    # X: 
    clp=$(printf "$cl" | tail -n $(($clc - 5)))

    #printf "%s\n%s\n" "$clp" "[cloc](/AlDanial/cloc)"
    printf "%s\n" "$clp"
    ;;
    wc)
    find schedul -name '*.py' -exec wc -l {} \; | grep -v migrations \
        | awk '{ 
            print $1, $2 
        }'
    ;;
    coverage) 
    which coverage > /dev/null && coverage report || echo '%[nocoverage]'
    ;;
    tuisrc) cat scripts/tui.sh ;;
    tree)
    tree -n -I "venv|_README|__pycache__|_a|_t|_aux|migrations|fixtures|requirements|openapi-fuzzer|lib|coverage|tests"
    ;;
    annotree) echo "%[..$1]" ;;
    testdo) grep -n -B 1 todo schedul/tests.py ;;
    *) echo "%[??$1]" ;;
    esac
    cd - > /dev/null
}


doc=$(for file in $(cat $mappath); do
    fdoc=$(cat "$partspath/$file")
    mlines=$(echo "$fdoc" | grep -n '%\[')
    #echo '==  '$file m 
    if [ -n "$mlines" ]; then
        # X: echo ..\n re limit<offset below
        doclen=$(echo "$fdoc" | wc -l)
        mcount=$(echo "$mlines" | wc -l)
        idx=1
        offset=1
        for line in $mlines; do

            n=$(echo $line | awk -F: '{ print $1 }')
            term=$(echo $line | awk -F: '{ print $2 }' \
                | sed 's/%\[\(.*\)\]/\1/')
            
            # X: 
            limit=$(($n - 1))
            #echo '==  't $term $doclen $n $idx $mcount $offset $limit

            if [ $limit -ge $offset ]; then
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
    echo "$doc" | $pager

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

