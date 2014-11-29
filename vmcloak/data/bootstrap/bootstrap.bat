call C:\vmcloak\settings.bat

echo Setting the DNS Server IP address.
netsh interface ip set dns name="Local Area Connection" static %DNSSERVER%

echo Setting static IP address.
netsh interface ip set address name="Local Area Connection" ^
    static %GUEST_IP% %GUEST_MASK% %GUEST_GATEWAY% 1

if "%BRIDGED%" == "yes" (
    netsh interface ip set address name="Local Area Connection 2" ^
        static %BRIDGEDIP% %BRIDGEDMASK% %BRIDGEDGATEWAY% 1
)

echo Installing 3rd party software.
call C:\vmcloak\deps.bat

echo Initiate VM hardening and start the guest.
C:\Python27\Python.exe C:\vmcloak\bootstrap.py
