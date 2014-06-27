#!/bin/bash
set -e

VBOXMANAGE="$1"

HOIFS="$($VBOXMANAGE list hostonlyifs)"

if [ -z "$HOIFS" ]; then
    "$VBOXMANAGE" hostonlyif create
    "$VBOXMANAGE" hostonlyif ipconfig vboxnet0 --ip 192.168.56.1
    echo "[x] Created vboxnet0 interface."
fi
