# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class DotNet(Dependency):
    name = "dotnet"
    depends = "wic"
    default = "4.0"
    recommended = True
    exes = [
        {
            "version": "4.0",
            "url": "https://cuckoo.sh/vmcloak/dotNetFx40_Full_x86_x64.exe",
            "sha1": "58da3d74db353aad03588cbb5cea8234166d8b99",
        },
        {
            "version": "4.5.1",
            "url": "https://cuckoo.sh/vmcloak/NDP451-KB2858728-x86-x64-AllOS-ENU.exe",
            "sha1": "5934dd101414bbc0b7f1ee2780d2fc8b9bec5c4d",
        },
        {
            "version": "4.6.1",
            "url": "https://cuckoo.sh/vmcloak/NDP461-KB3102436-x86-x64-AllOS-ENU.exe",
            "sha1": "83d048d171ff44a3cad9b422137656f585295866",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /passive /norestart")
        self.a.remove("C:\\setup.exe")

class DotNet40(DotNet, Dependency):
    """Backwards compatibility."""
    name = "dotnet40"
    recommended = False
