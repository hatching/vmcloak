call C:\vmcloak\settings.bat

echo Setting static IP address.
netsh interface ip set address name="Local Area Connection" ^
  static %HOSTONLYIP% %HOSTONLYMASK% %HOSTONLYGATEWAY% 1

if "%BRIDGED%" == "yes" (
    netsh interface ip set address name="Local Area Connection 2" ^
        static %BRIDGEDIP% %BRIDGEDMASK% %BRIDGEDGATEWAY% 1
)

echo Installing 3rd party software.
call C:\vmcloak\deps.bat

echo Initiate VM hardening.
C:\Python27\Python.exe C:\vmcloak\bootstrap.py

echo Starting the agent.
start C:\Python27\Pythonw.exe C:\vmcloak\agent.py
