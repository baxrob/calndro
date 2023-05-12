#!/bin/sh

cd $(dirname $0)/../_README

files="$(ls *.md) map"
gripid=
writepath=../test0.md
writepath=../readme_draft.md
bakdir=../_t/rdmd

trap 'echo INT; [ -n "$gripid" ] && kill $gripid; exit' INT

while true; do
    echo In: $(pwd)/ Watching: $files $(date)
    [ -n "$gripid" ] && kill $gripid
    grip $writepath 0.0.0.0 &
    gripid=$!
    echo $gripid
    
    # X: does sigint leave this process zombied ?- how best to kill ? wait pid?
    fname=$(inotifywait -q --format %w -e delete_self,close_write $files)
    [ $? -eq 0 ] || { echo fail $? $fname; break; }

    bakpath="$bakdir/$(date +%Y_%m_%d-%H_%M_%S-)$(basename $writepath)"
    bakpath="$bakdir/$(date +%Y_%m_%d-%H_%M-)$(basename $writepath)"
    cp -f "$writepath" "$bakpath"
    printf "\nbackup %s\n" "$bakpath"
    outpath="$writepath" ../scripts/stitch_readme.sh -q
    echo
done


