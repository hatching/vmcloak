# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import OperatingSystem
from vmcloak.rand import random_string
from vmcloak.verify import valid_serial_key

log = logging.getLogger(__name__)

class Windows7(OperatingSystem):
    name = 'win7'
    service_pack = 2
    mount = '/mnt/win7'
    nictype = '82540EM'
    osdir = os.path.join('sources', '$oem$', '$1')
    genisoargs = [
        '-no-emul-boot', '-iso-level', '2', '-udf', '-J', '-l', '-D', '-N',
        '-joliet-long', '-relaxed-filenames',
    ]

    def _autounattend_xml(self):
        values = {
            'PRODUCTKEY': self.serial_key,
            'COMPUTERNAME': random_string(8, 16),
            'USERNAME': random_string(8, 12),
            'PASSWORD': random_string(8, 16),
        }

        buf = open(os.path.join(self.path, 'autounattend.xml'), 'rb').read()
        for key, value in values.items():
            buf = buf.replace('@%s@' % key, value)

        return buf

    def isofiles(self, outdir, tmp_dir=None):
        with open(os.path.join(outdir, 'autounattend.xml'), 'wb') as f:
            f.write(self._autounattend_xml())

    def set_serial_key(self, serial_key):
        if serial_key and not valid_serial_key(serial_key):
            log.error('The provided serial key has an incorrect encoding.')
            log.info('Example encoding, AAAAA-BBBBB-CCCCC-DDDDD-EEEEE.')
            return False

        # https://technet.microsoft.com/en-us/library/jj612867.aspx
        self.serial_key = serial_key or '33PXH-7Y6KF-2VJC9-XBBR8-HVTHH'
        return True
