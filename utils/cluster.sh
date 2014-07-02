#!/bin/bash
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

case "$#" in
    1)
        COUNT="$1"
        STEP=1
        ;;

    2)
        COUNT="$1"
        STEP="$2"
        ;;

    0) ;&
    *)
        echo "Usage: $0 <count> [step]"
        exit 1
        ;;
esac

seq -w 1 "$COUNT"|xargs -P "$STEP" -I {} \
    ./vmcloak.py -s vmcloak.conf --hostonly-ip 192.168.56.1{} egg{}
