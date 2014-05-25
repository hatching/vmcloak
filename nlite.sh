#!/bin/sh
MOUNT=/mnt/nlite

if [ "$#" -eq 0 ]; then
    echo "Usage: ./nlite.sh <iso> [tempdir]"
    exit 1
elif [ "$#" -eq 1 ]; then
    IMAGE="$1"
    OUTIMAGE=$(echo $IMAGE|sed s/\.iso/\-new.iso/)
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

echo "Mounting the ISO image.."
sudo mkdir "$MOUNT" || cleanup 1
sudo mount -o loop,ro "$IMAGE" "$MOUNT" || cleanup 1

# Copy all files to our temporary directory, as
# mounted ISO files are read-only.
echo "Copying all files around.."
cp -r "$MOUNT"/* "$TEMPDIR" || cleanup 1
chmod -R +w "$TEMPDIR" || cleanup 1

# Overwrite certain files *according to the nLite tool.
echo "Overwriting various files.."
cp nlite/* "$TEMPDIR/i386/" || cleanup 1
cp boot.img "$TEMPDIR" || cleanup 1

# Make an ISO file with the updated file contents.
echo "Creating ISO image.."
mkisofs -quiet -b boot.img -no-emul-boot -boot-load-seg 1984 \
    -boot-load-size 4 -iso-level 2 -J -l -D -N -joliet-long \
    -relaxed-filenames -o "$OUTIMAGE" "$TEMPDIR" || cleanup 1

cleanup 0
echo $OUTIMAGE
