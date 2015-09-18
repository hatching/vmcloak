# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os
import tempfile

from vmcloak.abstract import OperatingSystem
from vmcloak.misc import ini_merge, ini_read, ini_write
from vmcloak.rand import random_string
from vmcloak.verify import valid_serial_key

log = logging.getLogger(__name__)

class WindowsXP(OperatingSystem):
    name = 'winxp'
    service_pack = 3
    mount = '/mnt/winxp'
    nictype = 'Am79C973'
    osdir = os.path.join('$oem$', '$1')
    genisoargs = [
        '-no-emul-boot', '-boot-load-seg', '1984', '-boot-load-size', '4',
        '-iso-level', '2', '-J', '-l', '-D', '-N', '-joliet-long',
        '-relaxed-filenames',
    ]

    def _winnt_sif(self):
        s = self.s
        values = {
            'PRODUCTKEY': self.serial_key,
            'COMPUTERNAME': random_string(8, 16),
            'FULLNAME': '%s %s' % (random_string(4, 8), random_string(4, 10)),
            'ORGANIZATION': '',
            'WORKGROUP': random_string(4, 8),
            # 'KBLAYOUT': s.keyboard_layout,
            'KBLAYOUT': 'US',
        }

        buf = open(os.path.join(self.path, 'winnt.sif'), 'rb').read()
        for key, value in values.items():
            buf = buf.replace('@%s@' % key, value)

        fd, winntsif = tempfile.mkstemp(suffix='.sif', dir=s.tempdir)
        os.write(fd, buf)
        os.close(fd)

        return winntsif

    def isofiles(self, outdir, tmp_dir=None):
        dst_winnt = os.path.join(outdir, 'i386', 'winnt.sif')

        winnt_sif = self._winnt_sif()

        # Merge the existing winnt.sif with our changes.
        mode, winnt = ini_read(dst_winnt)
        ini_merge(winnt, winnt_sif, overwrite=True)

        os.remove(winnt_sif)

        # There are a couple of optional values that should be set if they have
        # not already been set.
        winnt_opt_sif = os.path.join(self.path, 'winnt-opt.sif')
        ini_merge(winnt, winnt_opt_sif, overwrite=False)

        ini_write(dst_winnt, mode, winnt)

    def set_serial_key(self, serial_key):
        if not serial_key:
            log.error('No serial key has been provided - please do so!')
            return False

        if not valid_serial_key(serial_key):
            log.error('The provided serial key has an incorrect encoding.')
            log.info('Example encoding, AAAAA-BBBBB-CCCCC-DDDDD-EEEEE.')
            return False

        self.serial_key = serial_key
        return True
