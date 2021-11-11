call C:\vmcloak\settings.bat

echo Setting static IPv4 address.
netsh interface ip set address name="%INTERFACE%" ^
    static %GUEST_IP% %GUEST_MASK% %GUEST_GATEWAY% 1

echo Setting the DNS Server IP address to %DNSSERVER%
if "%DNSSERVER%" neq "" (
    netsh interface ip set dns name="%INTERFACE%" validate=no static %DNSSERVER%
    if "%DNSERVER2%" neq "" (
        echo Setting secondary DNS server IP to %DNSERVER2%
        netsh interface ip add dns name="%INTERFACE%" validate=no %DNSERVER2%
    )
)

echo Completely disable Windows Update.
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Wind4ws\CurrentVersion\WindowsUpdate\Auto Update" /v AUOptions /t REG_DWORD /d 1 /f
sc config wuauserv start= disabled
net stop wuauserv

echo Installing Python
start /w C:\vmcloak\%PYTHONINSTALLER% PrependPath=1 TargetDir=%PYTHONPATH% /passive

echo Copying agent file to c:\windows\system32\%AGENT_FILE%
copy c:\vmcloak\%AGENT_FILE% c:\windows\system32\%AGENT_FILE%

echo Setting the resolution.
%PYTHONPATH%\python.exe C:\vmcloak\resolution.py %RESO_WIDTH% %RESO_HEIGHT%

# Disable UAC
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v "EnableLUA" /t REG_DWORD /d 0 /f

echo Adding agent autorun key. Agent port: %AGENT_PORT%
reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v %AGENT_RUNKEY% /t REG_SZ /d "c:\windows\system32\%AGENT_FILE% -host 0.0.0.0 -port %AGENT_PORT%" /f

powershell -ExecutionPolicy bypass -File c:\vmcloak\genericsettings.ps1

echo Shutting down.
shutdown -s -t 0
