#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <count>"
    exit 1
fi

for i in $(seq 1 "$1"); do
    ./vmcloak.py -s vmcloak.conf --hostonly-ip 192.168.56.$((10+$i)) egg$i &
done

wait
