# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class IE9(Dependency):
    name = "ie9"
    default = "9"
    exes = [
        {
            "version": "9",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/IE9-Windows7-x64-enu.exe",
            "sha1": "5ace268e2812793e2232648f62cdf4be17b2b4dd",
        },
        {
            "version": "9",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/IE9-Windows7-x86-enu.exe",
            "sha1": "fb2b17cf1d22f3e2b2ad339c5bd78f8fab406d03",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")
        self.a.remove("C:\\setup.exe")
