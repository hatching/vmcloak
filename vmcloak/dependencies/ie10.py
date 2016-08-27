# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class IE10(Dependency):
    name = "ie10"
    default = "10"
    depends = [
        "kb:2729094", "kb:2731771", "kb:2533623", "kb:2670838", "kb:2786081",
        "kb:2639308", "kb:2834140",
    ]
    exes = [
        {
            "version": "10",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/IE10-Windows6.1-x64-en-us.exe",
            "sha1": "17d1eaca123e453269b12b20863fd5ce96727888",
        },
        {
            "version": "10",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/IE10-Windows6.1-x86-en-us.exe",
            "sha1": "e6552da75de95f6b1f7937c2bdb5fe14443dea2a",
        },
    ]

    def run(self):

        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")

        self.a.remove("C:\\setup.exe")
