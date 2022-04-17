#!/bin/sh

thispath="$(dirname "$0")"
basepath="$thispath/.."
partspath="${partspath:-"$thispath/../_README"}"
mapfilename=${mapfilename:-map}
mappath="$partspath/$mapfilename"
outpath=${outpath:-"$thispath/../README.md"}

echo $thispath $partspath $mapfilename $mappath $outpath

subs() {
    cd "$basepath"
    case $1 in
    cloc)
    cl=$(cloc --vcs=git) # "$(realpath "$basepath")")
    clc=$(printf "$cl" | wc -l)
    #echo $clc $basepath
    clp=$(printf "$cl" | tail -n $(($clc - 5)))
    #echo $cl
    #printf "%s\n" $clp
    #printf "%s\n\n" "$clp"
    #printf "%s\n%s\n" "$clp" "[cloc](/AlDanial/cloc)"

    printf "%s\n" "$clp"
    ;;
    wc)
    find schedul -name '*.py' -exec wc -l {} \; | grep -v migrations \
        | awk 'BEGIN { 
            print "lines", "\t", "file" 
            print "-----", "\t", "----" 
        } { 
            print $1, "\t", $2 
        }'
    ;;
    coverage) 
    which coverage && coverage report || echo '%[nocoverage]'
    ;;
    tuisrc) cat scripts/tui.sh ;;
    tree)
    tree -n -I "venv|_README|__pycache__|_a|_t|_aux|migrations|fixtures|requirements|openapi-fuzzer|lib|coverage|tests"
    ;;
    annotree) echo "%[..$1]" ;;
    testdo) grep -n -B 1 todo schedul/tests.py ;;
    default) echo "%[??$1]" ;;
    esac
    cd - > /dev/null
}


#doc=$(
for file in $(cat $mappath); do
    fdoc=$(cat "$partspath/$file")
    mlines=$(echo "$fdoc" | grep -n '%\[')
    echo -n $file m 
    printf "%s\n" $mlines
    for line in $mlines; do
        #echo l $line

        n=$(echo $line | awk -F: '{ print $1 }')
        term=$(echo $line | awk -F: '{ print $2 }' | sed 's/%\[\(.*\)\]/\1/')
        
        #term=$(echo $line | sed 's/%\[\(.*\)\]/\1/')
        echo t $term
        #st=$(printf "%s\\\\\n" "$(subs $term)")
        #sterm=$(subs $term | sed -z 's/\n/\\\n/g')

        sterm=$(subs $term | sed -z 's/\n/\\\n/g')
        #printf "%s\n" "$sterm"
        #subs $term
        #printf "subs $term
        #[ -n "$term" ] && fdoc=$(printf "%s" "$fdoc" | sed 's/%\['$term'\]/'"$(subs $term)"'/g')
        #[ -n "$term" ] && fdoc=$(printf "%s" "$fdoc" | sed 's/%\['$term'\]/'"$st"'/g')
        #[ -n "$term" ] && fdoc=$(printf "%s" "$fdoc" | sed "s~%\[$term\]~'$(subs $term)'~g")
        #[ -n "$term" ] && fdoc=$(printf "%s" "$fdoc" | awk '{ gsub(/%\[ )
        #[ -n "$term" ] && fdoc=$(printf "%s" "$fdoc" | sed 's~%\['$term'\]~'"$(subs $term)"'~g')
        #[ -n "$term" ] && fdoc=$(
        #    printf "%s" "$fdoc" | \
            #sed 's/%\['$term'\]/'"$sterm"'/g' 
            #sed 's/%\['$term'\]/'"$(subs $term | sed -z 's:\n:\\\n:g')"'/g' 
        #    awk '/%\['$term'\]/ { print '"$sterm"' }
        #        /^[^%]/ { print }'
        #)
    done
    #printf "%s" "$fdoc"
done
#printf "%s\n" "$bobo" | sed 's/%\['$x'\]/'"$(printf %s "$bozo" | sed -z 's:\n:\\\n:g')"'/g'
#)
#printf "\n%s" $doc
#printf "%s" "$doc" 
#printf "$doc" 
#echo $doc
exit
echo "$doc" | mdless

srcwc() {
    grep -n -B 2 todo ../schedul/tests.py
}
# 4139  find schedul -name '*.py' -exec cloc {} | grep ^Python \; 
# 4140  find schedul -name '*.py' -exec cloc {} \; | less
# 4141  find schedul -name '*.py' -exec wc {} && cloc {} \; | less
# 4142  find schedul -name '*.py' -exec wc {} cloc {} \; | less
# 4143  find schedul -name '*.py' -exec wc {}; cloc {} \; | less
# 4144  find schedul -name '*.py' -exec wc -l {} \; | less
# 4146  for i in $(find schedul -name '*.py'); do echo $i; wc -l $i; cloc $i | grep ^Python; done
# 4147  for i in $(find schedul -name '*.py' | grep -v migrations); do wc -l $i; cloc $i | grep ^Python; done | less
# 4148  for i in $(find schedul -name '*.py' | grep -v migrations); do wc -l $i; cloc $i | grep ^Python; done
# 4149  for i in $(find schedul -name '*.py' | grep -v migrations); do wc -l $i; cloc $i | grep -B 1 ^Python; done
# 4150  for i in $(find schedul -name '*.py' | grep -v migrations); do wc -l $i; cloc $i | grep -B 2 ^Python; done
# 4151  cloc manage.py | grep -B 2 Python | head -1 ; for i in $(find schedul -name '*.py' | grep -v migrations); do wc -l $i; cloc $i | grep ^Python; done
# 4152  clear
# 4153  cloc manage.py | grep -B 2 Python | head -1 ; for i in $(find schedul -name '*.py' | grep -v migrations); do wc -l $i; cloc $i | grep ^Python; done
# 4348  git ls-files  .. | wc -l | less
# 4349  git ls-files  .. | xargs wc -l
#
# 3497  grep -n '^\s*def test' tests.py |wc
# 3498  grep -n '^\s*def test' tests.py |wc -l
#


# X: %[\([^\]]*)] tui coverage cloc srcwc tree annotree testdo

#grep -d skip '%\[' * | sed 's/%\[\(.*\)\]/zz/'
#grep -d skip '%\[' * | sed 's/\%\[\([^\\]]*\)\]/zz/'
#grep -d skip '%\[' * | sed 's/\%\[\([^]]*\)\]/zz/'
#grep -d skip '%\[' * | sed 's/%\[\(.*\)\]/zz/'
#grep skip '%\[' * | sed 's/%\[\(.*\)\]/zz/'
#grep '%\[' * | sed 's/%\[\(.*\)\]/zz/'
#grep -d skip '%\[' * | sed 's/%\[\(.*\)\]/zz/'
#man grep
#grep -sh '%\[' * | sed 's/%\[\(.*\)\]/zz/'

#echo "$doc" | grep -sh '%\[' * | sed 's/%\[\(.*\)\]/"$rep"/'

#echo "$doc" | sed 's/%\[\(.*\)\]/"$("\1")"/g'

echo $(dirname "$0")/../README

cd "$(dirname "$0")"

dir=${1:-../_README}

segmap=$dir/map

verdir=$dir/ver
target=${2:-$verdir/README_$dt.md}

echo $dir $target
doc=$(for file in $(cat $segmap); do
    #echo $file
    #cat $file >> $target
    cat $dir/$file
done)


for i in srcwc cloc tuisrc covg ltree annotree testdo; do
#echo "$doc" | sed 's/%\[\(.*\)\]/"$rep"/'
    :
done


echo yo

# X: grip
# N: ttscoff/mdless
echo "$doc" | mdless
#echo $doc | less

date

file=../README.md

#diff $(
#dt=$(date +%Y%m%d-%H%M%S)
#echo "$doc" > GARBAGE-rdmd_$dt
#diff $tmpname $file

echo write to $file or ctrl-c ?

read foo

echo $file  
echo "$doc" > $file


# 

#less $target

