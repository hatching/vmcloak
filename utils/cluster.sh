#!/bin/bash
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <count>"
    exit 1
fi

for i in $(seq 1 "$1"); do
    ./vmcloak.py -s vmcloak.conf --hostonly-ip 192.168.56.$((10+$i)) egg$i &
done

wait
