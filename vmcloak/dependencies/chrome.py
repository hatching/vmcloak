# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.
# Chrome Dependency submitted by Jason Lewis.
# https://dl.google.com/dl/chrome/install/googlechromestandaloneenterprise.msi

from vmcloak.abstract import Dependency


class Chrome(Dependency):
    name = "chrome"
    default = "46.0.2490.80"
    exes = [{
        "version": "46.0.2490.80",
        "url": "https://cuckoo.sh/vmcloak/googlechromestandaloneenterprise.msi",
        "sha1": "a0ade494dda8911eeb68c9294c2dd0e3229d8f02",
    }, {
        "version": "latest",
        "arch": "x86",
        "urls": [
            "https://dl.google.com/edgedl/chrome/install/GoogleChromeStandaloneEnterprise.msi"
        ],
    }, {
        "version": "latest",
        "arch": "amd64",
        "urls": [
            "https://dl.google.com/edgedl/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
        ],
    }]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)

        # https://support.google.com/chrome/a/answer/6350036
        # this is not working properly :(
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Google\\Update\" "
            "/v UpdateDefault /t REG_DWORD /d 0 /f"
        )

        self.a.execute("msiexec /i C:\\%s /passive /norestart" % self.filename)
        self.a.remove("C:\\%s" % self.filename)

        # https://www.chromium.org/administrators/turning-off-auto-updates
        # this is not working properly :(
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Google\\Update\" "
            "/v AutoUpdateCheckPeriodMinutes /t REG_DWORD /d 0 /f"
        )
