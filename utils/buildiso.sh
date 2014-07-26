#!/bin/bash
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

set -e

if [ "$#" -lt 2 ]; then
    echo "Usage: ./buildiso.sh <mount> <winnt.sif> <outiso> <bootstrap>"
    exit 1
elif [ "$#" -eq 4 ]; then
    MOUNT="$1"
    WINNTSIF="$2"
    OUTIMAGE="$3"
    BOOTSTRAP="$4"
else
    echo "Invalid amount of arguments.."
    exit 1
fi

cleanup() {
    if [ -d "$TEMPDIR" ]; then
        echo "Removing tempdir.."
        rm -rf "$TEMPDIR"
    fi
    if [ $1 -eq 1 ]; then
        exit 1
    fi
}

# When a command fails we do a bit of cleanup.
trap "cleanup 1" ERR

TEMPDIR="$(mktemp -d)"

# Copy all files to our temporary directory, as
# mounted ISO files are read-only.
echo "Copying files around.."
./utils/cplower.py "$MOUNT" "$TEMPDIR"
chmod -R +w "$TEMPDIR"

echo "Overwriting various files.."
cp data/boot.img "$TEMPDIR"

# Merge the original winnt.sif file with our settings. Note that we have a
# set of configuration values that we overwrite whether they're already
# present in the original winnt.sif or not, and also a set of optional values
# which will only be used if they're not present in the configuration already.
./utils/inimodify.py "$TEMPDIR/i386/winnt.sif" merge "$WINNTSIF" --overwrite
./utils/inimodify.py "$TEMPDIR/i386/winnt.sif" merge data/winnt-opt.sif

echo "Installing bootstrap files and copying dependencies.."
OSDIR="$TEMPDIR/\$oem\$/\$1"
mkdir -p "$OSDIR"
cp data/bootstrap/* "$OSDIR"
cp -r "$BOOTSTRAP"/* "$OSDIR"

if [ -f /usr/bin/mkisofs ]; then
    ISOTOOL=/usr/bin/mkisofs
elif [ -f /usr/bin/genisoimage ]; then
    ISOTOOL=/usr/bin/genisoimage
else
    echo "Either mkisofs or genisoimage is required!"
    cleanup 1
fi

# Make an ISO file with the updated file contents.
echo "Creating ISO image.."
$ISOTOOL -quiet -b boot.img -no-emul-boot -boot-load-seg 1984 \
    -boot-load-size 4 -iso-level 2 -J -l -D -N -joliet-long \
    -relaxed-filenames -o "$OUTIMAGE" "$TEMPDIR"

cleanup 0
