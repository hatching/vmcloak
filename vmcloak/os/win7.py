# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path
import shutil

from vmcloak.abstract import OperatingSystem
from vmcloak.verify import valid_serial_key

log = logging.getLogger(__name__)


class Windows7(OperatingSystem):
    name = 'win7'
    mount = '/mnt/win7'
    genisoargs = [
        '-no-emul-boot', '-iso-level', '2', '-udf', '-J', '-l', '-D', '-N',
        '-joliet-long', '-relaxed-filenames',
    ]

    def configure(self, s):
        pass

    def isofiles(self, outdir, tmp_dir=None):
        dst_unattend = os.path.join(outdir, 'autounattend.xml')
        shutil.copy(os.path.join(self.path, 'autounattend.xml'), dst_unattend)

    def set_serial_key(self, serial_key):
        if serial_key and not valid_serial_key(serial_key):
            log.error('The provided serial key has an incorrect encoding.')
            log.info('Example encoding, AAAAA-BBBBB-CCCCC-DDDDD-EEEEE.')
            return False

        # https://technet.microsoft.com/en-us/library/jj612867.aspx
        self.serial_key = serial_key or '33PXH-7Y6KF-2VJC9-XBBR8-HVTHH'
        return True
