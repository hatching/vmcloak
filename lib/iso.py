# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import shutil
import subprocess
import tempfile

from lib.misc import copy_directory_lower, ini_merge, ini_read, ini_write


def buildiso(mount, winnt_sif, iso_out, bootstrap):
    """Builds an ISO file containing all our modifications."""
    tempdir = tempfile.mkdtemp()

    # Copy all files to our temporary directory as mounted iso files are
    # read-only and we need lowercase (aka case-insensitive) filepaths.
    copy_directory_lower(mount, tempdir)

    # Copy the boot image.
    shutil.copy(os.path.join('data', 'boot.img'), tempdir)

    dst_winnt = os.path.join(tempdir, 'i386', 'winnt.sif')

    # Merge the existing winnt.sif with our changes.
    mode, winnt = ini_read(dst_winnt)
    ini_merge(winnt, winnt_sif, overwrite=True)

    # There are a couple of optional values that should be set if they have
    # not already been set.
    ini_merge(winnt, os.path.join('data', 'winnt-opt.sif'), overwrite=False)

    ini_write(dst_winnt, mode, winnt)

    osdir = os.path.join(tempdir, '$oem$', '$1')
    os.makedirs(osdir)

    for fname in os.listdir(os.path.join('data', 'bootstrap')):
        shutil.copy(os.path.join('data', 'bootstrap', fname),
                    os.path.join(osdir, fname))

    shutil.copytree(bootstrap, os.path.join(osdir, 'bootstrap'))

    if os.path.isfile('/usr/bin/genisoimage'):
        isocreate = '/usr/bin/genisoimage'
    elif os.path.isfile('/usr/bin/mkisofs'):
        isocreate = '/usr/bin/mkisofs'
    else:
        print '[-] Either genisoimage or mkisofs is required!'
        shutil.rmtree(tempdir)
        return False

    try:
        args = [
            isocreate, '-quiet', '-b', 'boot.img', '-no-emul-boot',
            '-boot-load-seg', '1984', '-boot-load-size', '4',
            '-iso-level', '2', '-J', '-l', '-D', '-N', '-joliet-long',
            '-relaxed-filenames', '-o', iso_out, tempdir
        ]

        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        print '[-] Error creating ISO file: %s' % e
        shutil.rmtree(tempdir)
        return False

    shutil.rmtree(tempdir)
    return True
