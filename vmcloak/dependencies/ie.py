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
        },
        {
            "version": "10_x64",
            "url": "http://download.microsoft.com/download/C/E/0/CE0AB8AE-E6B7-43F7-9290-F8EB0EA54FB5/IE10-Windows6.1-x64-en-us.exe",
            "sha1": "17d1eaca123e453269b12b20863fd5ce96727888",
            "requires": [
                {
                    "version": "KB2729094",
                    "url": "http://download.microsoft.com/download/6/C/A/6CA15546-A46C-4333-B405-AB18785ABB66/Windows6.1-KB2729094-v2-x64.msu",
                },
                {
                    "version": "KB2731771",
                    "url": "http://download.microsoft.com/download/9/F/E/9FE868F6-A0E1-4F46-96E5-87D7B6573356/Windows6.1-KB2731771-x64.msu",
                },
                {
                    "version": "KB2533623",
                    "url": "http://download.microsoft.com/download/F/1/0/F106E158-89A1-41E3-A9B5-32FEB2A99A0B/Windows6.1-KB2533623-x64.msu",
                },
                {
                    "version": "KB2670838",
                    "url": "http://download.microsoft.com/download/1/4/9/14936FE9-4D16-4019-A093-5E00182609EB/Windows6.1-KB2670838-x64.msu",
                },
                {
                    "version": "KB2786081",
                    "url": "http://download.microsoft.com/download/1/8/F/18F9AE2C-4A10-417A-8408-C205420C22C3/Windows6.1-KB2786081-x64.msu",
                },
            ]
        },
    ]

    def run(self):

        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")
        
        self.wait_process_exit("IE10-Windows6.1-x64-en-us.exe")
        
