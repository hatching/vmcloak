# Copyright (C) 2016-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Win7sp(Dependency):
    name = "win7sp"
    default = "1"
    exes = [{
        "version": "sp1",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/0/A/F/0AFB5316-3062-494A-AB78-7FB0D4461357/windows6.1-KB976932-X64.exe",
            "https://cuckoo.sh/vmcloak/windows6.1-KB976932-X64.exe",
        ],
        "sha1": "74865ef2562006e51d7f9333b4a8d45b7a749dab",
    }, {
        "version": "sp1",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/0/A/F/0AFB5316-3062-494A-AB78-7FB0D4461357/windows6.1-KB976932-X86.exe",
            "https://cuckoo.sh/vmcloak/windows6.1-KB976932-X86.exe",
        ],
        "sha1": "c3516bc5c9e69fee6d9ac4f981f5b95977a8a2fa",
    }]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart")
        self.a.remove("C:\\setup.exe")
