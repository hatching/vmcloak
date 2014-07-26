#!/bin/bash
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.
set -e

VBOXMANAGE="$1"

HOIFS="$($VBOXMANAGE list hostonlyifs)"

if [ -z "$HOIFS" ]; then
    "$VBOXMANAGE" hostonlyif create
    "$VBOXMANAGE" hostonlyif ipconfig vboxnet0 --ip 192.168.56.1
    echo "[x] Created vboxnet0 interface."
fi
