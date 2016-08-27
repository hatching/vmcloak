# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Win7sp(Dependency):
    name = "win7sp"
    exes = [
        {
            "version": "1",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/windows6.1-KB976932-X64.exe",
            "sha1": "74865ef2562006e51d7f9333b4a8d45b7a749dab",
        },
        {
            "version": "1",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/windows6.1-KB976932-X86.exe",
            "sha1": "c3516bc5c9e69fee6d9ac4f981f5b95977a8a2fa",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart")
        self.a.remove("C:\\setup.exe")
