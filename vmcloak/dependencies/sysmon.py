# Copyright (C) 2017-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Sysmon(Dependency):
    name = "sysmon"
    description = "Monitoring and logging system activity"
    default = "8.0.0"
    exes = [{
        "version": "6.0.2",
        "arch": "amd64",
        "url": "https://cuckoo.sh/vmcloak/Sysmon64.exe",
        "sha1": "ce9edbea1937d593bf6cba4d9ca57d66f1680fdf",
    }, {
        "version": "6.0.2",
        "arch": "x86",
        "url": "https://cuckoo.sh/vmcloak/Sysmon.exe",
        "sha1": "b97d720eca991bd96d6a8d60ea93ee163e09178d",
    }, {
        "version": "8.0.0",
        "arch": "amd64",
        "url": "https://cuckoo.sh/vmcloak/Sysmon64-8.0.0.exe",
        "sha1": "173014bedc7d852a4cee961440ffaf06fa716353",
    }, {
        "version": "8.0.0",
        "arch": "x86",
        "url": "https://cuckoo.sh/vmcloak/Sysmon-8.0.0.exe",
        "sha1": "8cc70223e7f667387d9792a5183129734d3b5501",
    }]

    def run(self):
        self.upload_dependency("C:\\sysmon.exe")
        self.a.execute("C:\\sysmon.exe /accepteula /i /l /n /r")
        self.a.remove("C:\\sysmon.exe")
