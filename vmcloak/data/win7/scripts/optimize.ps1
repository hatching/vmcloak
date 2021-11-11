# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

Write-Host "Optimizing Windows 7 settings"

###
### Security
###

Write-Host "Applying Windows 7 security tweaks"

# Hide Action Center icon
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v HideSCAHealth /t REG_DWORD /d 1 /f

# Disable security center notifications
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Security Center" /v FirewallOverride /t REG_DWORD /d 0 /f
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Security Center" /v AntiVirusOverride /t REG_DWORD /d 0 /f

# Disable Roaming security checks
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\System" /v CompatibleRUPSecurity /t REG_DWORD /d 0 /f
reg add "HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\System" /v CompatibleRUPSecurity /t REG_DWORD /d 0 /f

# Deactivate the secured shell modus
reg add "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v PreXPSP2ShellProtocolBehavior /t REG_DWORD /d 1 /f

# Enable TLS 1.1/1.2
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\WinHttp\DefaultSecureProtocols" /v DefaultSecureProtocols /d 0xAA0 /t REG_DWORD /f
reg add "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Internet Settings\WinHttp\DefaultSecureProtocols" /v DefaultSecureProtocols /d 0xAA0 /t REG_DWORD /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Client" /v DisabledByDefault /d 0 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client" /v DisabledByDefault /d 0 /f
