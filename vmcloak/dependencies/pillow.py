# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Pillow(Dependency):
    name = "pillow"
    recommended = True
    default = "2.9.0"
    exes = [{
        "version": "2.9.0",
        "urls": [
            "https://pypi.python.org/packages/2.7/P/Pillow/Pillow-2.9.0.win32-py2.7.exe",
            "https://cuckoo.sh/vmcloak/Pillow-2.9.0.win32-py2.7.exe",
        ],
        "sha1": "1138f6db53b54943cbe7cf237c4df7e9255ca034",
    }, {
        "version": "3.4.2",
        "urls": [
            "https://pypi.python.org/packages/59/59/ece120265d3918f75b43dda870566e58d675c3e865bf63f520e7f01425e5/Pillow-3.4.2.win32-py2.7.exe",
        ],
        "sha1": "46778e4c41cb721b035fb72b82e17bcaba94c077",
    }]

    def run(self):
        self.upload_dependency("C:\\pillow.exe")
        self.a.execute("C:\\pillow.exe", async=True)
        self.a.click("Setup", "&Next >")
        self.a.click("Setup", "&Next >")
        self.a.click("Setup", "&Next >")
        self.a.click("Setup", "Finish")

        self.wait_process_exit("pillow.exe")
        self.a.remove("C:\\pillow.exe")
