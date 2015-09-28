# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Pillow(Dependency):
    name = "pillow"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/Pillow-2.9.0.win32-py2.7.exe",
            "sha1": "1138f6db53b54943cbe7cf237c4df7e9255ca034",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\pillow.exe")
        self.a.execute("C:\\pillow.exe", async=True)
        self.a.click("Setup", "&Next >")
        self.a.click("Setup", "&Next >")
        self.a.click("Setup", "&Next >")
        self.a.click("Setup", "Finish")

        self.wait_process_exit("pillow.exe")
        self.a.remove("C:\\pillow.exe")
