#!/bin/sh

cd "$(dirname "$0")"

dir=${1:-../_README}

segmap=$dir/map

echo $dir $target

false && for file in $(cat $segmap); do
    #echo $file
    #cat $file >> $target
    cat $dir/$file
done | less

doc=$(for file in $(cat $segmap); do
    #echo $file
    #cat $file >> $target
    cat $dir/$file
done)

srcwc() {
    grep -n -B 2 todo ../schedul/tests.py
}
cloc() {
    cd ..
    cloc --vcs=git
    cd -
}
tuisrc() {
    :
}
covg() {
    :
}
ltree() {
    :
}
annotree() {
    :
}
testdo() {
    :
}
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
verdir=$dir/ver
target=${2:-$verdir/README_$dt.md}

#less $target

