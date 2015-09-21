# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

config = """
<Configuration Product="ProPlus">
    <Display Level="none" CompletionNotice="no" SuppressModal="yes" AcceptEula="yes" />
    <PIDKEY Value="%(serial_key)s" />
</Configuration>
"""

class Office2007(Dependency):
    name = "office2007"

    def init(self):
        self.isopath = None
        self.serialkey = None

    def check(self):
        if not self.isopath:
            log.error("Please provide a serial key for Office 2007.")
            return False

        if not os.path.isfile(self.isopath):
            log.error("Please provide the Office 2007 installer ISO file.")
            return False

    def run(self):
        self.disable_autorun()

        self.m.attach_iso(self.isopath)
        self.a.upload("C:\\config.xml", config % dict(serial_key=self.serialkey))
        self.a.execute("D:\\setup.exe /config C:\\config.xml")

        # Wait until setup.exe is no longer running.
        self.wait_process_exit("setup.exe")

        self.a.remove("C:\\config.xml")
        self.m.detach_iso()
