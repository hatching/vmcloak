#!/bin/bash
# Copyright (C) 2014-2015 Mohsen Ahmadi.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
set -ue

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

function getabs () {
    echo "$(find $1 -name '*.iso')"
}

USER="pwnslinger"
MEDIA="/media/$USER/D268B33068B31269/windows"

declare -A MOUNT_POINTS=( ["winxpx86"]="$MEDIA/winxp/x86" ["winxpx64"]="$MEDIA/winxp/x64" 
                        ["win7x86"]="$MEDIA/win7/x86" ["win7x64"]="$MEDIA/win7/x64" 
                        ["win81x86"]="$MEDIA/win81/x86" ["win81x64"]="$MEDIA/win81/x64" 
                        ["win10x86"]="$MEDIA/win10/x86" ["win10x64"]="$MEDIA/win10/x64" 
                        )

for mount in "${!MOUNT_POINTS[@]}"; do
    MOUNT_DIR="/mnt/$mount"
    if [ ! -d $MOUNT_DIR ]; then
        mkdir -p $MOUNT_DIR
    else
        echo "Mounting the $mount in /mnt/$mount"
        MPoint="$(getabs "${MOUNT_POINTS[$mount]}")"

        findmnt $MOUNT_DIR 2> /dev/null
        if [ $? -ne 0  ]; then
            /bin/mount -o loop,ro $MPoint $MOUNT_DIR 2>/dev/null
        fi
    fi
done
