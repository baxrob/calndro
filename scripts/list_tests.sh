#!/bin/sh

cd $(dirname $0)/../schedul

views="detail list notify log  emailtoken loggedinuser openapi service"
methods="post get patch delete  expired emailtoken enlog"

for view in $views; do
    for meth in $methods; do
        g="${view}_${meth}"
        grep -q $g tests.py || continue
        printf "\n=== $g ===\n"
        grep -E "test_$g|^class" tests.py
    done
done
