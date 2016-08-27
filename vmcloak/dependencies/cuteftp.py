# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import time

from vmcloak.abstract import Dependency

class Cuteftp(Dependency):
    name = "cuteftp"
    default = "9.0.5"
    exes = [
        {
            "version": "9.0.5",
            "url": "https://cuckoo.sh/vmcloak/cuteftp.exe",
            "sha1": "1d8497b3f31f76168eb2573efe60dcefb3422e1d",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
        self.a.execute("C:\\%s /S" % self.filename, async=True)

        time.sleep(1)
        self.a.click("InstallShield Wizard", "&Next >")
        self.a.click("InstallShield Wizard", "&Yes")
        self.a.click("InstallShield Wizard", "&Next >")
        time.sleep(1)
        self.a.click("InstallShield Wizard", "Finish")

        self.wait_process_exit("cuteftp.exe")

        self.a.remove("C:\\%s" % self.filename)
