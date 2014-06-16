#!/bin/bash
set -e
MOUNT=/mnt/vmcloak

if [ "$#" -eq 0 ]; then
    echo "Usage: ./nlite.sh <iso> [outiso] [tempdir]"
    exit 1
elif [ "$#" -eq 1 ]; then
    IMAGE="$1"
    OUTIMAGE="$(echo -n "$IMAGE"|sed s/\.iso/\-new.iso/)"
    TEMPDIR="$(mktemp -d)"
elif [ "$#" -eq 2 ]; then
    IMAGE="$1"
    OUTIMAGE="$2"
    TEMPDIR="$(mktemp -d)"
elif [ "$#" -eq 3 ]; then
    IMAGE="$1"
    OUTIMAGE="$2"
    TEMPDIR="$3"
fi

cleanup() {
    if [ -d "$TEMPDIR" ]; then
        echo "Removing tempdir.."
        rm -rf "$TEMPDIR"
    fi
    if [ -d "$MOUNT" ]; then
        echo "Unmounting mount.."
        sudo umount "$MOUNT"
        sudo rm -r "$MOUNT"
    fi
    if [ $1 -eq 1 ]; then
        exit 1
    fi
}

# When a command fails we do a bit of cleanup.
trap "cleanup 1" ERR

echo "Mounting the ISO image.."
sudo mkdir -p "$MOUNT"
sudo mount -o loop,ro "$IMAGE" "$MOUNT"

# Copy all files to our temporary directory, as
# mounted ISO files are read-only.
echo "Copying files around.."
./utils/cplower.py "$MOUNT" "$TEMPDIR"
chmod -R +w "$TEMPDIR"

# Overwrite certain files according to the nLite tool.
echo "Overwriting various files.."
cp boot.img "$TEMPDIR"

# Merge the original winnt.sif file with our settings.
./utils/inimodify.py "$TEMPDIR/i386/winnt.sif" merge winnt-configured.sif

echo "Installing bootstrap files.."
OSDIR="$TEMPDIR/\$oem\$/\$1"
mkdir -p "$OSDIR"
cp bootstrap/* "$OSDIR"

# Make an ISO file with the updated file contents.
echo "Creating ISO image.."
mkisofs -quiet -b boot.img -no-emul-boot -boot-load-seg 1984 \
    -boot-load-size 4 -iso-level 2 -J -l -D -N -joliet-long \
    -relaxed-filenames -o "$OUTIMAGE" "$TEMPDIR"

cleanup 0
echo $OUTIMAGE
