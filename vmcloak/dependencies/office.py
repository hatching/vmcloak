# Copyright (C) 2014-2016 Jurriaan Bremer.
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

class Office(Dependency):
    name = "office"

    def init(self):
        self.isopath = None
        self.serialkey = None

    def check(self):
        if not self.serialkey:
            log.error("Please provide a serial key for Office.")
            return False

        if not self.isopath or not os.path.isfile(self.isopath):
            log.error("Please provide the Office installer ISO file.")
            return False

    def run(self):
        if self.i.vm == "virtualbox":
            self.disable_autorun()
            self.m.attach_iso(self.isopath)

        self.a.upload("C:\\config.xml", config % dict(serial_key=self.serialkey))
        self.a.execute("D:\\setup.exe /config C:\\config.xml")

        # Wait until setup.exe is no longer running.
        self.wait_process_exit("setup.exe")

        self.a.remove("C:\\config.xml")

        if self.i.vm == "virtualbox":
            self.m.detach_iso()

class Office2007(Office, Dependency):
    """Backwards compatibility."""
    name = "office2007"
