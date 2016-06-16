# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import time

from vmcloak.abstract import Dependency

class IE10(Dependency):
    name = "ie10"
    default = "10"
    depends = ["KB:2729094", "KB:2731771", "KB:2533623", "KB:2670838", "KB:2786081", "KB:2639308", "KB:2834140"]
    exes = [
        {
            "version": "10",
            "target": "win7x64",
            "url": "http://download.microsoft.com/download/C/E/0/CE0AB8AE-E6B7-43F7-9290-F8EB0EA54FB5/IE10-Windows6.1-x64-en-us.exe",
            "sha1": "17d1eaca123e453269b12b20863fd5ce96727888",
        },
        {
            "version": "10",
            "target": "win7",
            "url": "https://download.microsoft.com/download/5/2/B/52BE95BF-22D8-4415-B644-0FDF398F6D96/IE10-Windows6.1-KB2859903-x86.msu",
            "sha1": "edef436d2ee7b71663607df7fa13e2647e9b0d6a",
        },
    ]

    def run(self):

        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")

        self.a.remove("C:\\setup.exe")
