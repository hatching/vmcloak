# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
# Chrome Dependency submitted by Jason Lewis.

from vmcloak.abstract import Dependency

class RemoveTooltips(Dependency):
    name = "removetooltips"
    description = "Removes balloon tooltips for new users"
    exes = [
        {
            "url": "https://cuckoo.sh/vmcloak/MicrosoftFixit50048.msi",
            "sha1": "0de68031b1c1d17bf6851b13f2d083ee61b6b533",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\MicrosoftFixit50048.msi")
        self.a.execute("msiexec /i C:\\MicrosoftFixit50048.msi /passive /norestart")
        self.a.remove("C:\\MicrosoftFixit50048.msi")
