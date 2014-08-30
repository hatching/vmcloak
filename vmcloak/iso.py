# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import logging
import shutil
import subprocess
import tempfile

from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.misc import copytreelower, copytreeinto
from vmcloak.misc import ini_merge, ini_read, ini_write
from vmcloak.paths import get_path

log = logging.getLogger()


def buildiso(mount, winnt_sif, iso_out, bootstrap, tmp_dir=None):
    """Builds an ISO file containing all our modifications."""
    tempdir = tempfile.mkdtemp(dir=tmp_dir)

    # Copy all files to our temporary directory as mounted iso files are
    # read-only and we need lowercase (aka case-insensitive) filepaths.
    copytreelower(mount, tempdir)

    # Copy the boot image.
    shutil.copy(os.path.join(VMCLOAK_ROOT, 'data', 'boot.img'), tempdir)

    dst_winnt = os.path.join(tempdir, 'i386', 'winnt.sif')

    # Merge the existing winnt.sif with our changes.
    mode, winnt = ini_read(dst_winnt)
    ini_merge(winnt, winnt_sif, overwrite=True)

    # There are a couple of optional values that should be set if they have
    # not already been set.
    winnt_opt_sif = os.path.join(VMCLOAK_ROOT, 'data', 'winnt-opt.sif')
    ini_merge(winnt, winnt_opt_sif, overwrite=False)

    ini_write(dst_winnt, mode, winnt)

    osdir = os.path.join(tempdir, '$oem$', '$1')
    os.makedirs(os.path.join(osdir, 'vmcloak'))

    data_bootstrap = os.path.join(VMCLOAK_ROOT, 'data', 'bootstrap')
    for fname in os.listdir(data_bootstrap):
        shutil.copy(os.path.join(data_bootstrap, fname),
                    os.path.join(osdir, 'vmcloak', fname))

    copytreeinto(bootstrap, osdir)

    isocreate = get_path('genisoimage')
    if not isocreate:
        log.error('Either genisoimage or mkisofs is required!')
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
        log.error('Error creating ISO file: %s', e)
        shutil.rmtree(tempdir)
        return False

    shutil.rmtree(tempdir)
    return True
