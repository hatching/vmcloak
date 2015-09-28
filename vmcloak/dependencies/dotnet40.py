# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class DotNet40(Dependency):
    name = "dotnet40"
    depends = "wic",
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/dotNetFx40_Full_x86_x64.exe",
            "sha1": "58da3d74db353aad03588cbb5cea8234166d8b99",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\dotnet40.exe")
        self.a.execute("C:\\dotnet40.exe /passive /norestart")
        self.a.remove("C:\\dotnet40.exe")
