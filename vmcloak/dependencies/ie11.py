# Copyright (C) 2016-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import time

from vmcloak.abstract import Dependency
from vmcloak.exceptions import DependencyError

log = logging.getLogger(__name__)

_depends = [
    "kb:2670838", "kb:2639308", "kb:2533623", "kb:2731771", "kb:2729094",
    "kb:2786081", "kb:2882822", "kb:2888049", "kb:2834140",
]

ie11settings_ps = """
reg add "HKLM\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_EUPP_GLOBAL_FORCE_DISABLE" /v iexplore.exe /d 1 /t REG_DWORD /f
# disable first use popup:
# http://www.geoffchappell.com/notes/windows/ie/firstrun.htm
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main" /v DisableFirstRunCustomize /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\Software\Microsoft\Internet Explorer\Main" /v RunOnceComplete /t REG_DWORD /d 1 /f
reg add "HKEY_LOCAL_MACHINE\Software\Microsoft\Internet Explorer\Main" /v RunOnceHasShown /t REG_DWORD /d 1 /f

# Disables auto update:
# https:/social.technet.microsoft.com/Forums/en-US/c49c96f7-247e-4404-b80f-3df5253dc13f/how-to-uncheck-install-new-versions-automatically-from-internet-explorer-11-from-sccm-2012?forum=ieitprocurrentver
reg add "HKEY_LOCAL_MACHINE\Software\Microsoft\Internet Explorer\Main" /v EnableAutoUpgrade /t REG_DWORD /d 0 /f

#   0        My Computer
#   1        Local Intranet Zone
#   2        Trusted sites Zone
#   3        Internet Zone
#   4        Restricted Sites Zone
# https://support.microsoft.com/en-us/help/182569/internet-explorer-security-zones-registry-entries-for-advanced-users
# disable protected mode for all zones for all users
# https://superuser.com/questions/1031225/what-is-the-registry-setting-to-enable-protected-mode-in-a-specific-zone
# Sets permissions in every zone to 'permitted'
$values = @("1001", "1004", "1200", "1201", "1206", "1207", "1208", "1209", "120A", "120B", "1400", "1402",
"1405", "1406", "1407", "1408", "1409", "1601", "1604", "1605", "1606", "1607", "1608", "1609", "160A", "1800",
"1802", "1803", "1804", "1805", "1806", "1807", "1808", "1809", "180A", "180C", "180D", "180E", "180F", "1A02",
"1A03", "1A04", "1A05", "1A06", "1A10", "2000", "2005", "2100", "2101", "2102", "2103", "2104", "2105", "2106",
"2200", "2201", "2300", "2301", "2400", "2401", "2402", "2500", "2600", "2700", "2004", "2001", "2007", "2107")

foreach ($zone in (0, 1, 2, 3, 4)) {
    foreach ($value in $values) {
	reg add ("HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\" + $zone) /v $value /t REG_DWORD /d 0 /f
    }
}

# Disable protected mode
# https:/www.eightforums.com/tutorials/31977-internet-explorer-enhanced-protected-mode-turn-off.html
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main" /v Isolation /t REG_SZ /d PMIL /f

# weaken security
# http:/www.geoffchappell.com/notes/windows/ie/featurecontrol.htm
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN" /v iexplore.exe /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_RESTRICT_FILEDOWNLOAD" /v iexplore.exe /t REG_DWORD /d 0 /f

reg add "HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Security" /v "Safety Warning Level" /t REG_SZ /d Low /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Security" /v Sending_Security /t REG_SZ /d Low /f
reg add "HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Security" /v Viewing_Security /t REG_SZ /d Low /f

# "You are about to be redirected to a connection that is not secure."
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v WarnOnHTTPSToHTTPRedirect /t REG_DWORD /d 0 /f

# "You are about to view pages over a secure connection."
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v WarnOnZoneCrossing /t REG_DWORD /d 0 /f

# "Internet Explorer - Security Warning"
# "The publisher could not be verified."
reg add "HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Download" /v CheckExeSignatures /t REG_SZ /d no /f

# Disable "fix security settings" warning
# https:/answers.microsoft.com/en-us/ie/forum/ie8-windows_other/when-opening-internet-explorer-constantly-getting/e591c609-1e50-4210-a770-2474beb1430f?auth=1
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main\Security" /v DisableFixSecuritySettings /t REG_DWORD /d 1 /f

reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main\Security" /v DisableSecuritySettingsCheck /t REG_DWORD /d 1 /f

# Disable IE8 IE9+ smartscreen filter:
# https:/www.sevenforums.com/tutorials/1406-internet-explorer-smartscreen-filter-turn-off.html
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\PhishingFilter" /v EnabledV8 /t REG_DWORD /d 0 /f

reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\PhishingFilter" /v EnabledV9 /t REG_DWORD /d 0 /f

reg add "HKCU\Software\Microsoft\Internet Explorer\BrowserEmulation" /v MSCompatibilityMode /t REG_DWORD /d 0 /f

# set default webpage and disable IE default browser check:
reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main" /v Check_Associations /t REG_SZ /d no /f

reg add "HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Internet Explorer\Main" /v "Start Page" /t REG_SZ /d about:blank /f

#Set the window size to maximized
reg add "HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Main" /v "Window_Placement" /t REG_BINARY /d "2C0000000200000003000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF2400000024000000AA04000089020000" /f

#Disable addons/plugins
reg add "HKEY_CURRENT_USER\Software\Microsoft\Internet Explorer\Main" /v "Enable Browser Extensions" /t REG_SZ /d "no" /f

#Disable 'addon is ready to use' notification
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Ext" /v "IgnoreFrameApprovalCheck" /t REG_DWORD /d 1 /f
"""

class IE11(Dependency):
    name = "ie11"
    default = "11"
    os_depends = {
        "win7x64": _depends,
        "win7x86": _depends,
        "win10x64": "optimizeos"
    }

    tags = ["browser_internet_explorer"]

    no_exe = ["win10x64"]
    exes = [{
        "version": "11",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/7/1/7/7179A150-F2D2-4502-9D70-4B59EA148EAA/IE11-Windows6.1-x64-en-us.exe",
            "https://hatching.dev/hatchvm/IE11-Windows6.1-x64-en-us.exe",
        ],
        "sha1": "ddec9ddc256ffa7d97831af148f6cc45130c6857",
    }, {
        "version": "11",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/9/2/F/92FC119C-3BCD-476C-B425-038A39625558/IE11-Windows6.1-x86-en-us.exe",
            "https://hatching.dev/hatchvm/IE11-Windows6.1-x86-en-us.exe",
        ],
        "sha1": "fefdcdde83725e393d59f89bb5855686824d474e",
    }]

    def _run_once(self):
        # Run ie once so that settings/files/etc created on the first run
        # are created.
        self.a.execute(
            '"c:\\Program Files\\Internet explorer\\iexplore.exe"', cucksync=True
        )
        # Wait until process exists and then leave it to run for a few seconds.
        self.wait_process_appear("iexplore.exe")
        time.sleep(5)
        self.a.killprocess("iexplore.exe", force=False)
        try:
            self.wait_process_exit("iexplore.exe", timeout=60)
        except TimeoutError as e:
            log.debug(e)
            self.a.killprocess("iexplore.exe", force=True)
            self.wait_process_exit("iexplore.exe", timeout=30)

    def _run_win7(self):
        self.upload_dependency("C:\\setup.exe")
        try:
            res = self.a.execute("C:\\setup.exe /quiet /norestart /update-no")
            exit_code = res.get("exit_code")
            # Exit codes for success must reboot and already installed.
            if exit_code not in (0, 3010, 40008):
                raise DependencyError(
                    "Failed to install IE11. Installer returned unexpected "
                    f"non-zero exit code: {exit_code}"
                )
        finally:
            self.a.remove("C:\\setup.exe")

        log.debug("Rebooting for IE11 install to take effect")
        # First reboot before applying registry changes. Otherwise the
        # changes will somehow be gone/not apply. IE11 is only available after
        # the reboot.
        self.installer.do_reboot()
        log.debug("Applying settings to optimize IE11")
        res = self.run_powershell_strings(ie11settings_ps)
        if res.get("stderr"):
            log.error(
                "Failed to apply on or more IE11 registry settings. "
                f"Script return errors. {res.get('stderr')}"
            )
        self._run_once()

    def _run_win10(self):
        log.debug("Applying settings to optimize IE11")
        self.run_powershell_strings(ie11settings_ps)
        self._run_once()

    def run(self):
        if self.i.osversion in ("win7x64", "win7x86"):
            self._run_win7()
        elif self.i.osversion == "win10x64":
            self._run_win10()
