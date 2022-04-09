#!/bin/sh

cd "$(dirname "$0")"

dir=${1:-../_README}
segmap=$dir/map

echo $dir $target

for file in $(cat $segmap); do
    #echo $file
    #cat $file >> $target
    cat $dir/$file
done | less

# 
verdir=$dir/ver
target=${2:-$verdir/README_$dt.md}

#less $target

