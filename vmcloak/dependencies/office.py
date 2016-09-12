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
    <Setting Id="AUTO_ACTIVATE" Value="%(activate)s" />
</Configuration>
"""

class Office(Dependency):
    name = "office"

    def init(self):
        self.isopath = None
        self.serialkey = None
        self.activate = None

    def check(self):
        if not self.serialkey:
            log.error("Please provide a serial key for Office.")
            return False

        if not self.isopath or not os.path.isfile(self.isopath):
            log.error("Please provide the Office installer ISO file.")
            return False

        if not self.activate:
            self.activate = 0
            log.info("Defaulting activate to False")
            return True
        elif self.activate not in ["0", "1"]:
            log.error(
                "Please keep activate value 0 or 1. You had %s.",
                self.activate
            )
            return False

    def run(self):
        if self.i.vm == "virtualbox":
            self.disable_autorun()
            self.m.attach_iso(self.isopath)

        self.a.upload(
            "C:\\config.xml",
            config % dict(serial_key=self.serialkey, activate=self.activate)
        )
        self.a.execute("D:\\setup.exe /config C:\\config.xml")

        # Wait until setup.exe is no longer running.
        self.wait_process_exit("setup.exe")

        self.a.remove("C:\\config.xml")

        if self.i.vm == "virtualbox":
            self.m.detach_iso()

class Office2007(Office, Dependency):
    """Backwards compatibility."""
    name = "office2007"
