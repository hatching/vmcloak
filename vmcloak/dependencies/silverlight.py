# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Silverlight(Dependency):
    name = "silverlight"
    exes = [
        {
            "url": "https://cuckoo.sh/vmcloak-files/Silverlight_Developer_x86.exe",
            "sha1": "f87518a85e90050cbe4b4b76308f105c7b37acdc",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /q /doNotRequireDRMPrompt /noupdate")
        self.a.remove("C:\\setup.exe")
