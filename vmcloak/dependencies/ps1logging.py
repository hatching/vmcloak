# Copyright (C) 2017-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class PS1Logging(Dependency):
    name = "ps1logging"
    default = "3109118"
    depends = [
        "win7sp", "dotnet:4.6.1", "kb:2819745", "kb:3109118"
    ]

    def run(self):
        # Set registry keys to enable PowerShell enchanced logging

        # Enable Module Logging for all modules
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging\" "
            "/v EnableModuleLogging /t REG_DWORD /d 00000001 /f /reg:64"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging\\ModuleNames\" "
            "/v * /t REG_SZ /d * /f /reg:64"
        )

        # Enable Script Block Logging
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging\" "
            "/v EnableScriptBlockLogging /t REG_DWORD /d 00000001 /f /reg:64"
        )

        # Enable Transcription and log to a central location
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Microsoft\\Windows\\PowerShell\\Transcription\" "
            "/v EnableTranscripting /t REG_DWORD /d 00000001 /f /reg:64"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Microsoft\\Windows\\PowerShell\\Transcription\" "
            "/v OutputDirectory /t REG_SZ /d \"C:\PSTranscipts\" /f /reg:64"
        )
        self.a.execute(
            "reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\"
            "Policies\\Microsoft\\Windows\\PowerShell\\Transcription\" "
            "/v EnableInvocationHeader /t REG_DWORD /d 00000001 /f /reg:64"
        )
