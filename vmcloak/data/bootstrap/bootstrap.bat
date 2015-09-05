call C:\vmcloak\settings.bat

echo Setting the DNS Server IP address.
netsh interface ip set dns name="Local Area Connection" static %DNSSERVER%

echo Setting static IP address.
netsh interface ip set address name="Local Area Connection" ^
    static %GUEST_IP% %GUEST_MASK% %GUEST_GATEWAY% 1

echo Installing 3rd party software.
call C:\vmcloak\deps.bat

if "%RUNEXEC%" neq "" (
    call C:\vmcloak\%RUNEXEC%
)

echo Completely disable Windows updates.
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" /v AUOptions /t REG_DWORD /d 1 /f
sc config wuauserv start= disabled
net stop wuauserv

echo Initiate VM hardening and start the guest.
if "%DEBUG%" == "yes" (
    C:\Python27\Python.exe C:\vmcloak\bootstrap.py
) else (
    C:\Python27\Pythonw.exe C:\vmcloak\bootstrap.py
)
