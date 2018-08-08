# Copyright (C) 2016-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class IE11(Dependency):
    name = "ie11"
    default = "11"
    depends = [
        "kb:2670838", "kb:2639308", "kb:2533623", "kb:2731771", "kb:2729094",
        "kb:2786081", "kb:2882822", "kb:2888049", "kb:2834140",
    ]
    exes = [{
        "version": "11",
        "target": "win7x64",
        "urls": [
            "https://download.microsoft.com/download/7/1/7/7179A150-F2D2-4502-9D70-4B59EA148EAA/IE11-Windows6.1-x64-en-us.exe",
            "https://cuckoo.sh/vmcloak/IE11-Windows6.1-x64-en-us.exe",
        ],
        "sha1": "ddec9ddc256ffa7d97831af148f6cc45130c6857",
    }, {
        "version": "11",
        "target": "win7x86",
        "urls": [
            "https://download.microsoft.com/download/9/2/F/92FC119C-3BCD-476C-B425-038A39625558/IE11-Windows6.1-x86-en-us.exe",
            "https://cuckoo.sh/vmcloak/IE11-Windows6.1-x86-en-us.exe",
        ],
        "sha1": "fefdcdde83725e393d59f89bb5855686824d474e",
    }]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /quiet /norestart /update-no")
        self.a.remove("C:\\setup.exe")

        # disable first use popup:
        # http://www.geoffchappell.com/notes/windows/ie/firstrun.htm
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v DisableFirstRunCustomize /t REG_DWORD /d 1 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v RunOnceComplete /t REG_DWORD /d 1 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v RunOnceHasShown /t REG_DWORD /d 1 /f"
        )

        # disable auto update:
        # https://social.technet.microsoft.com/Forums/en-US/c49c96f7-247e-4404-b80f-3df5253dc13f/how-to-uncheck-install-new-versions-automatically-from-internet-explorer-11-from-sccm-2012?forum=ieitprocurrentver
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v EnableAutoUpgrade /t REG_DWORD /d 0 /f"
        )

        #   0        My Computer
        #   1        Local Intranet Zone
        #   2        Trusted sites Zone
        #   3        Internet Zone
        #   4        Restricted Sites Zone
        # https://support.microsoft.com/en-us/help/182569/internet-explorer-security-zones-registry-entries-for-advanced-users
        # disable protected mode for all zones for all users
        # https://superuser.com/questions/1031225/what-is-the-registry-setting-to-enable-protected-mode-in-a-specific-zone
        for zone in range(0, 5):
            self.a.execute(
                "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
                "Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\%s\" "
                "/v 2500 /t REG_DWORD /d 3 /f" % zone
            )

        # Disable protected mode
        # https://www.eightforums.com/tutorials/31977-internet-explorer-enhanced-protected-mode-turn-off.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v Isolation /t REG_SZ /d \"PMIL\" /f"
        )

        # weaken IE11 security
        # http://www.geoffchappell.com/notes/windows/ie/featurecontrol.htm
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\\"
            "FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN\" "
            "/v \"iexplore.exe\" /t REG_DWORD /d 0 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\\"
            "FeatureControl\\FEATURE_RESTRICT_FILEDOWNLOAD\" "
            "/v \"iexplore.exe\" /t REG_DWORD /d 0 /f"
        )

        # Disable "fix security settings" warning
        # https://answers.microsoft.com/en-us/ie/forum/ie8-windows_other/when-opening-internet-explorer-constantly-getting/e591c609-1e50-4210-a770-2474beb1430f?auth=1
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\\Security\" "
            "/v DisableFixSecuritySettings /t REG_DWORD /d 1 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\\Security\" "
            "/v DisableSecuritySettingsCheck /t REG_DWORD /d 1 /f"
        )

        # Disable IE8 IE9+ smartscreen filter:
        # https://www.sevenforums.com/tutorials/1406-internet-explorer-smartscreen-filter-turn-off.html
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\PhishingFilter\" "
            "/v EnabledV8 /t REG_DWORD /d 0 /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\PhishingFilter\" "
            "/v EnabledV9 /t REG_DWORD /d 0 /f"
        )

        # set default webpage and disable IE default browser check:
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v \"Check_Associations\" /t REG_SZ /d \"no\" /f"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\Software\\Policies\\"
            "Microsoft\\Internet Explorer\\Main\" "
            "/v \"Start Page\" /t REG_SZ /d \"about:blank\" /f"
        )
