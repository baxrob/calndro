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

echo yo

echo "$doc" | less
#echo $doc | less

date

file=../README.md

#diff $(

echo write to $file or ctrl-c ?

read foo

echo "$doc" > $file


# 
verdir=$dir/ver
target=${2:-$verdir/README_$dt.md}

#less $target

