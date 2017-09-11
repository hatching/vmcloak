# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Sysmon(Dependency):
    name = "sysmon"
    description = "Monitoring and logging system activity"
    default = "6.0.2"
    exes = [
        {
            "version": "6.0.2",
            "arch": "amd64",
            "url": "https://cuckoo.sh/vmcloak/Sysmon64.exe",
            "sha1": "849b8dfaf9159afdc14d514b2243d4d5ba2ff9a4",
        },
        {
            "version": "6.0.2",
            "arch": "x86",
            "url": "https://cuckoo.sh/vmcloak/Sysmon.exe",
            "sha1": "199f1773123652d7e958468c280426aff6e16d78",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\sysmon.exe")
        self.a.execute("C:\\sysmon.exe /accepteula /i /l /n /r")
        self.a.remove("C:\\sysmon.exe")