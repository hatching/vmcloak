call C:\vmcloak\settings.bat

echo Setting static IPv4 address.
netsh interface ip set address name="%INTERFACE%" ^
    static %GUEST_IP% %GUEST_MASK% %GUEST_GATEWAY% 1

echo Setting the DNS Server IP address.
if "%DNSSERVER%" neq "" (
    netsh interface ip set dns name="%INTERFACE%" static %DNSSERVER%
)

echo Completely disable Windows Update.
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" /v AUOptions /t REG_DWORD /d 1 /f
sc config wuauserv start= disabled
net stop wuauserv

echo Installing Python 2.7.6.
start C:\vmcloak\python-2.7.6.msi
C:\vmcloak\click.exe "Python 2.7.6 Setup" "Next >"
C:\vmcloak\click.exe "Python 2.7.6 Setup" "Next >"
C:\vmcloak\click.exe "Python 2.7.6 Setup" "Next >"
C:\vmcloak\click.exe "Python 2.7.6 Setup" "Finish"

echo Installing the Agent.
copy C:\vmcloak\agent.py C:\agent.py
if "%DEBUG%" == "yes" (
    set PYTHON=C:\Python27\Python.exe
) else (
    set PYTHON=C:\Python27\Pythonw.exe
)

echo Setting the resolution.
C:\Python27\Python.exe C:\vmcloak\resolution.py %RESO_WIDTH% %RESO_HEIGHT%

reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v Agent /t REG_SZ /d "%PYTHON% C:\agent.py 0.0.0.0 %AGENT_PORT%" /f

echo Shutting down.
shutdown -s -t 0
