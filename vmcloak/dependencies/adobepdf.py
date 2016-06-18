# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class AdobePdf(Dependency):
    name = "adobepdf"
    default = "9.0.0"
    exes = [
        {
            "version": "9.0.0",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr90_en_US.exe",
            "sha1": "8faabd08289b9a88023f71136f13fc4bd3290ef0",
        },
        {
            "version": "11.0.9",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11009_en_US.exe",
            "sha1": "53b367bff07a63ee07cf1cd090360b75d3fc6bfb",
        },
        {
            "version": "11.0.10",
            "url": "http://cuckoo.sh/vmcloak/AdbeRdr11010_en_US.exe",
            "sha1": "98b2b838e6c4663fefdfd341dfdc596b1eff355c",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
        self.a.execute(
            "C:\\%s /sAll /msi /norestart /quiet ALLUSERS=1 EULA_ACCEPT=YES" %
            self.filename
        )

        self.a.remove("C:\\%s" % self.filename)

        # add needed registry keys to skip Licence Agreement
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\9.0\\AdobeViewer\" "
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\9.0\\AdobeViewer\" "
            "/v EULA /t REG_DWORD /d 1 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\9.0\\AdobeViewer\" "
            "/v Launched /t REG_DWORD /d 1 /f"
        )

        # man : https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/
        # we don't care about updates really
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\AVGeneral\" "
            "/v bCheckForUpdatesAtStartup /t REG_DWORD /d 0 /f"
        )

        # allow URL access
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\TrustManager\\cDefaultLaunchURLPerms\" "
        )
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\TrustManager\\cDefaultLaunchURLPerms\" "
            "/v iURLPerms /t REG_DWORD /d 2 /f"
        )

        # FIXME: really needed ?
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\9.0\\Security\\cDigSig\\cCustomDownload\" "
            "/v bLoadSettingsFromURL /t REG_DWORD /d 0 /f"
        )

class Adobe9(AdobePdf, Dependency):
    """Backwards compatibility."""
    name = "adobe9"
