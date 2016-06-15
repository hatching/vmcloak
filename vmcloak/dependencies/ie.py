# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import time

from vmcloak.abstract import Dependency

class IE(Dependency):
    name = "ie"
    default = "11_x64"
    exes = [
        {
            "version": "11_x64",
            "url": "http://download.microsoft.com/download/7/1/7/7179A150-F2D2-4502-9D70-4B59EA148EAA/IE11-Windows6.1-x64-en-us.exe",
            "sha1": "ddec9ddc256ffa7d97831af148f6cc45130c6857",
            "depends": ["KB2729094", "KB2731771", "KB2533623", "KB2670838", "KB2786081"], 
        },
        {
            "version": "10_x64",
            "url": "http://download.microsoft.com/download/C/E/0/CE0AB8AE-E6B7-43F7-9290-F8EB0EA54FB5/IE10-Windows6.1-x64-en-us.exe",
            "sha1": "17d1eaca123e453269b12b20863fd5ce96727888",
            "requires": [

            ]
        },
    ]

    def run(self):

        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")
        
        self.wait_process_exit("IE10-Windows6.1-x64-en-us.exe")
        
