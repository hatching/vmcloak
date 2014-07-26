#!/bin/bash
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

set -e

VBOXMANAGE="$1"

HOIFS="$($VBOXMANAGE list hostonlyifs)"

if [ -z "$HOIFS" ]; then
    "$VBOXMANAGE" hostonlyif create
    "$VBOXMANAGE" hostonlyif ipconfig vboxnet0 --ip 192.168.56.1
    echo "[x] Created vboxnet0 interface."
fi
