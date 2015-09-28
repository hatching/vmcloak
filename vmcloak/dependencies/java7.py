# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Java7(Dependency):
    name = "java7"
    exes = [
        {
            "url": "http://cuckoo.sh/vmcloak/jdk-7-windows-i586.exe",
            "sha1": "2546a78b6138466b3e23e25b5ca59f1c89c22d03",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\java7.exe")
        self.a.execute("C:\\java7.exe", async=True)
        self.a.click("Java(TM) SE Development Kit 7 - Setup", "&Next >")
        self.a.click("Java(TM) SE Development Kit 7 - Custom Setup", "&Next >")
        self.a.click("Java Setup - Destination Folder", "&Next >")
        self.a.click("Java(TM) SE Development Kit 7 - Complete", "&Finish")

        # Wait until java7.exe & javaw.exe are no longer running.
        self.wait_process_exit("java7.exe")
        self.wait_process_exit("javaw.exe")

        # Wait for iexplore to appear and kill it.
        self.wait_process_appear("iexplore.exe")
        self.a.killprocess("iexplore.exe")

        self.a.remove("C:\\java7.exe")
