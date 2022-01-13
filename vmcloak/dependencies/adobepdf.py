# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import time

from vmcloak.abstract import Dependency
from vmcloak.exceptions import DependencyError

log = logging.getLogger(__name__)

_adobedefaulthandler_ps1 = """
# Make adobe the default PDF handler https://eddiejackson.net/wp/?p=15400
control /name Microsoft.DefaultPrograms /page pageDefaultProgram\pageAdvancedSettings?pszAppName=Adobe%20Reader%20XI%20`(%VERSION%`)
$wshell = New-Object -ComObject wscript.shell
For ($a=0; $a -le 10; $a++) {
  Start-Sleep -s 1
  If ($proc.MainWindowHandle -ne 0) {
    Start-Sleep -s 1
    $wshell.SendKeys("{TAB} {Enter}")
    Break
  }
}

"""

class AdobePdf(Dependency):
    name = "adobepdf"
    default = "11.0.8"
    recommended = True
    tags = ["adobepdf", "pdfreader"]
    exes = [{
        "version": "9.0.0",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr90_en_US.exe",
        "sha1": "8faabd08289b9a88023f71136f13fc4bd3290ef0",
    }, {
        "version": "9.1.0",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr910_en_US.exe",
        "sha1": "1e0db06c84d89c8f58b543a41ec35b133de7ea19",
    }, {
        "version": "9.2.0",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr920_en_US.exe",
        "sha1": "4b6207b018cf2be2f49d1f045ff369eb3bee88da",
    }, {
        "version": "9.3.0",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr930_en_US.exe",
        "sha1": "98cacd6069e78a0dd1ef87ce24e59716fecf8aa0",
    }, {
        "version": "9.3.3",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr933_en_US.exe",
        "sha1": "b1ed1d350db97ddd562606449804e705d4ffe1c7",
    }, {
        "version": "9.3.4",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr934_en_US.exe",
        "sha1": "e3bb8eff9d199ab1f4b5f7a10e514a74e0384ca0",
    }, {
        "version": "9.4.0",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr940_en_US.exe",
        "sha1": "4652a454056b2323097a6357292db3af239bb610",
    }, {
        "version": "9.5.0",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr950_en_US.exe",
        "sha1": "e46000691a6dbcd7892078b46c8ee13613683545",
    }, {
        "version": "10.1.4",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr1014_en_US.exe",
        "sha1": "fe6808d5d11e94dc5581f33ed386ce552f0c84d6",
    }, {
        "version": "11.0.0",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.00/en_US/AdbeRdr11000_en_US.exe",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.00/en_US/AdbeRdr11000_en_US.exe",
            "https://cuckoo.sh/vmcloak/AdbeRdr11000_en_US.exe",
        ],
        "sha1": "e7dd04e037c40b160a2f01db438dba9ea0b12c52",
        "filename": "AdbeRdr11000_en_US.exe",
    }, {
        "version": "11.0.2",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr11002_en_US.exe",
        "sha1": "e1d9e57f08e169fb1c925f8ded93e5f5efe5cda3",
    }, {
        "version": "11.0.3",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr11003_en_US.exe",
        "sha1": "9c2b6903b000ecf2869e1555bc6e1b287e6176bf",
    }, {
        "version": "11.0.4",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr11004_en_US.exe",
        "sha1": "9c295c16d374735bf292ef6c630c9ab392c22500",
    }, {
        "version": "11.0.6",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr11006_en_US.exe",
        "sha1": "6a3d5b494b4ed6e11fc7d917afc03eaf05d4a6aa",
    }, {
        "version": "11.0.7",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr11007_en_US.exe",
        "sha1": "3e08c3f6daad59f463227590cc438b3906648f5e",
    }, {
        "version": "11.0.8",
        "url": "https://hatching.io/hatchvm/AdbeRdr11008_en_US.exe",
        "sha1": "3e889258ea2000337bbe180d81317d44f617a292",
    }, {
        "version": "11.0.9",
        "url": "https://cuckoo.sh/vmcloak/AdbeRdr11009_en_US.exe",
        "sha1": "53b367bff07a63ee07cf1cd090360b75d3fc6bfb",
    }, {
        "version": "11.0.10",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.10/en_US/AdbeRdr11010_en_US.exe",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.10/en_US/AdbeRdr11010_en_US.exe",
            "https://cuckoo.sh/vmcloak/AdbeRdr11010_en_US.exe",
        ],
        "sha1": "98b2b838e6c4663fefdfd341dfdc596b1eff355c",
        "filename": "AdbeRdr11010_en_US.exe",
    }, {
        "version": "11.0.11",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.11/misc/AdbeRdrUpd11011.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.11/misc/AdbeRdrUpd11011.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11011.msp",
        ],
        "sha1": "182eb5b4ca71e364f62e412cdaec65e7937417e4",
        "filename": "AdbeRdrUpd11011.msp",
    }, {
        "version": "11.0.12",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.12/misc/AdbeRdrUpd11012.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.12/misc/AdbeRdrUpd11012.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11012.msp",
        ],
        "sha1": "c5a5f2727dd7dabe0fcf96ace644751ac27872e7",
        "filename": "AdbeRdrUpd11012.msp",
    }, {
        "version": "11.0.13",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.13/misc/AdbeRdrUpd11013.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.13/misc/AdbeRdrUpd11013.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11013.msp",
        ],
        "sha1": "89317596ffe50e35c136ef204ac911cbf83b14d9",
        "filename": "AdbeRdrUpd11013.msp",
    }, {
        "version": "11.0.14",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.14/misc/AdbeRdrUpd11014.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.14/misc/AdbeRdrUpd11014.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11014.msp",
        ],
        "sha1": "d7b990117d8a6bbc4380663b7090cd60d2103079",
        "filename": "AdbeRdrUpd11014.msp",
    }, {
        "version": "11.0.16",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.16/misc/AdbeRdrUpd11016.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.16/misc/AdbeRdrUpd11016.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11016.msp",
        ],
        "sha1": "ca825c50ed96a2fec6056c94c1bb44eedbaed890",
        "filename": "AdbeRdrUpd11016.msp",
    }, {
        "version": "11.0.17",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.17/misc/AdbeRdrUpd11017.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.17/misc/AdbeRdrUpd11017.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11017.msp",
        ],
        "sha1": "c5fe501856be635566e864fe76f6d6a7ff3874ca",
        "filename": "AdbeRdrUpd11017.msp",
    }, {
        "version": "11.0.18",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.18/misc/AdbeRdrUpd11018.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.18/misc/AdbeRdrUpd11018.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11018.msp",
        ],
        "sha1": "420d64c064cd9904836a60066a222c64b0ea060e",
        "filename": "AdbeRdrUpd11018.msp",
    }, {
        "version": "11.0.19",
        "urls": [
            "http://ardownload.adobe.com/pub/adobe/reader/win/11.x/11.0.19/misc/AdbeRdrUpd11019.msp",
            "ftp://ftp.adobe.com/pub/adobe/reader/win/11.x/11.0.19/misc/AdbeRdrUpd11019.msp",
            "https://cuckoo.sh/vmcloak/AdbeRdrUpd11019.msp",
        ],
        "sha1": "98fdf7a15fb2486ee7257767296d4f7a0a62ac92",
        "filename": "AdbeRdrUpd11019.msp",
    }]

    def _run_once(self):
        v = self.version.split(".")[0]
        self.a.execute(
            f'"c:\\Program Files (x86)\\Adobe\\Reader {v}.0\\Reader'
            f'\\AcroRd32.exe"', cucksync=True
        )
        # Wait until process exists and then leave it to run for a few seconds.
        # The 'preparing for first use' dialog can take some time.
        self.wait_process_appear("AcroRd32.exe")
        time.sleep(120)
        self.a.killprocess("AcroRd32.exe", force=False)
        try:
            self.wait_process_exit("AcroRd32.exe", timeout=30)
        except TimeoutError as e:
            log.debug(e)
            self.a.killprocess("AcroRd32.exe", force=True)
            self.wait_process_exit("AcroRd32.exe", timeout=30)

    def _make_adobe_default(self):
        ps1 = _adobedefaulthandler_ps1.replace("%VERSION%", self.version)
        self.run_powershell_strings(ps1)

    def run(self):
        if self.version.startswith("11") and self.filename.endswith(".msp"):
            log.debug(
                "We have a MSI upgrade package, we need the vanilla "
                "AdbeRdr installer."
            )

            orig_exe, self.exe = self.exe, None
            for exe in self.exes:
                if exe["version"] == "11.0.0":
                    self.exe = exe
                    break
            else:
                log.error(
                    "Could not find AdbeRdr v11.0 which is required for %s",
                    self.filename
                )
                raise DependencyError

            self.download()

            self.upload_dependency("C:\\%s" % self.filename)
            self.a.execute(
                "C:\\%s -nos_oC:\\AdobeFiles -nos_ne" % self.filename
            )
            self.a.remove("C:\\%s" % self.filename)

            self.exe = orig_exe
            self.download()
            self.upload_dependency("C:\\%s" % self.filename)
            self.a.execute(
                "msiexec /i C:\\AdobeFiles\\AcroRead.msi "
                "/update C:\\%s /norestart /passive "
                "ALLUSERS=1 EULA_ACCEPT=YES" % self.filename
            )
            self.a.remove("C:\\%s" % self.filename)
            self.a.remove("C:\\AdobeFiles")
        else:
            self.upload_dependency("C:\\%s" % self.filename)
            try:
                exit_code = self.a.execute(
                    "C:\\%s /sPb /rs /rps /norestart OWNERSHIP_STATE=0 "
                    "ALLUSERS=1 EULA_ACCEPT=YES SUPPRESS_APP_LAUNCH=YES" %
                    self.filename
                ).get("exit_code")
                if exit_code not in (0, 3010):
                    raise DependencyError(
                        f"Failed to install Adobepdf {self.version}. "
                        f"Installer returned unexpected non-zero "
                        f"exit code: {exit_code}"
                    )
            finally:
                self.a.remove("C:\\%s" % self.filename)

        key_version = self.version.split('.')[0]
        # add needed registry keys to skip Licence Agreement
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\%s.0\\AdobeViewer\" "
            "/v EULA /t REG_DWORD /d 1 /f" % key_version
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\WOW6432Node\\"
            "Adobe\\Acrobat Reader\\%s.0\\AdobeViewer\" "
            "/v Launched /t REG_DWORD /d 1 /f" % key_version
        )
        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader"
            "\\%s.0\\AdobeViewer\" "
            "/v EULA /t REG_DWORD /d 1 /f " % key_version
        )

        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader"
            "\\%s.0\\AdobeViewer\" "
            "/v Launched /t REG_DWORD /d 1 /f " % key_version
        )

        # man : https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/
        # we don't care about updates really
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\%s.0\\AVGeneral\" "
            "/v bCheckForUpdatesAtStartup /t REG_DWORD /d 0 /f" %
            key_version
        )

        # disable the updater completely
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/Updater-Win.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\FeatureLockDown\" "
            "/v bUpdater /t REG_DWORD /d 0 /f" % key_version
        )

        # disable the sandboxing (protected mode)
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/AppSec/protectedmode.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\FeatureLockDown\" "
            "/v bProtectedMode /t REG_DWORD /d 0 /f" % key_version
        )
        self.a.execute(
            "reg add \"HKCU\\SOFTWARE\\Adobe\\Acrobat Reader\\%s.0\\"
            "Privileged\" /v bProtectedMode /t REG_DWORD /d 0 /f" % key_version
        )
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/AppSec/protectedview.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\FeatureLockDown\" "
            "/v iProtectedView /t REG_DWORD /d 0 /f" % key_version
        )

        self.a.execute(
            "reg add \"HKCU\\SOFTWARE\\Adobe\\Acrobat Reader\\%s.0\\"
            "TrustManager\" /v iProtectedView /t REG_DWORD /d 0 /f"
        )

        # disable enchanced security
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/AppSec/enhanced.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\FeatureLockDown\" "
            "/v bEnhancedSecurityStandalone /t REG_DWORD /d 0 /f" %
            key_version
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\FeatureLockDown\" "
            "/v bEnhancedSecurityInBrowser /t REG_DWORD /d 0 /f" %
            key_version
        )

        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader\\%s.0\\"
            "TrustManager\" /v bEnhancedSecurityStandalone "
            "/t REG_DWORD /d 0 /f" % key_version
        )
        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader\\%s.0\\"
            "TrustManager\" /v bEnhancedSecurityInBrowser "
            "/t REG_DWORD /d 0 /f" % key_version
        )

        # allow URL access
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/FeatureLockdown.html
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\%s.0\\TrustManager\\cDefaultLaunchURLPerms\" "
            "/v iURLPerms /t REG_DWORD /d 2 /f" % key_version
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\"
            "FeatureLockDown\\cDefaultLaunchURLPerms\" "
            "/v iUnknownURLPerms /t REG_DWORD /d 2 /f" % key_version
        )

        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader\\%s.0\\"
            "TrustManager\\cDefaultLaunchURLPerms\" /v iURLPerms "
            "/t REG_DWORD /d 2 /f" % key_version
        )
        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader\\%s.0\\"
            "TrustManager\\cDefaultLaunchURLPerms\" /v iUnknownURLPerms "
            "/t REG_DWORD /d 2 /f" % key_version
        )

        # allow opening of all embedded files
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/Attachments.html
        self.a.execute(
            "reg delete \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\"
            "FeatureLockDown\\cDefaultLaunchAttachmentPerms\" "
            "/v tBuiltInPermList /f" % key_version
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\"
            "FeatureLockDown\\cDefaultLaunchAttachmentPerms\" "
            "/v iUnlistedAttachmentTypePerm /t REG_DWORD /d 2 /f" %
            key_version
        )

        self.a.execute(
            "reg add \"HKCU\\Software\\Adobe\\Acrobat Reader\\%s.0\\"
            "Attachments\\cDefaultLaunchURLPerms\" "
            "/v iUnlistedAttachmentTypePerm /t REG_DWORD /d 2 /f" % key_version
        )

        # enable flash content
        # https://www.adobe.com/devnet-docs/acrobatetk/tools/PrefRef/Windows/FeatureLockdown.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Adobe\\Acrobat Reader\\%s.0\\FeatureLockDown\" "
            "/v bEnableFlash /t REG_DWORD /d 1 /f" % key_version
        )

        # Disable periodic trust anchor downloading from Adobe.
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Software\\Adobe\\"
            "Acrobat Reader\\%s.0\\Security\\cDigSig\\cAdobeDownload\" "
            "/v bLoadSettingsFromURL /t REG_DWORD /d 0 /f" % key_version
        )
        self._make_adobe_default()
        self._run_once()

class Adobe9(AdobePdf, Dependency):
    """Backwards compatibility."""
    name = "adobe9"
    recommended = False
