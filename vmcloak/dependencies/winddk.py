# Copyright (C) 2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

class WinDDK(Dependency):
    name = "winddk"
    components=[
        # Windows headers and libraries and a complete set of build tools for
        # building Windows drivers
        "{45273B30-342D-4748-494A-4B4C4D4E4F50}",

        # General purpose and device specific tools
        "{45393536-343C-4748-494A-4B4C4D4E4F50}",

        # Debugger
        "{45302A29-4546-4748-494A-4B4C4D4E4F50}",
    ]

    def init(self):
        self.isopath = None

    def check(self):
        if not self.isopath or not os.path.isfile(self.isopath):
            log.error("Please provide GRMWDK_EN_7600_1.ISO")
            return False

    def run(self):
        self.disable_autorun()
        self.m.attach_iso(self.isopath)

        cs = " ".join(self.components)
        # KitSetup loves to crash when executed directly
        self.a.execute("cmd /k D:\\KitSetup.exe /install %s /ui-level EXPRESS" % cs)
        self.wait_process_exit("KitSetup.exe")

        self.m.detach_iso()
