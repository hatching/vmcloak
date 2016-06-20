# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class IE11(Dependency):
    name = "ie11"
    default = "11"
    depends = [
        "KB:2670838", "KB:2639308", "KB:2533623", "KB:2731771", "KB:2729094",
        "KB:2786081", "KB:2882822", "KB:2888049", "KB:2834140",
    ]
    exes = [
        {
            "version": "11",
            "target": "win7x64",
            "url": "http://cuckoo.sh/vmcloak/IE11-Windows6.1-x64-en-us.exe",
            "sha1": "ddec9ddc256ffa7d97831af148f6cc45130c6857",
        },
        {
            "version": "11",
            "target": "win7",
            "url": "http://cuckoo.sh/vmcloak/IE11-Windows6.1-x86-en-us.exe",
            "sha1": "fefdcdde83725e393d59f89bb5855686824d474e",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")
        self.a.remove("C:\\setup.exe")
