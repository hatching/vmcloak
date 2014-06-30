call C:\settings.bat

echo Setting static IP address.
rem TODO Allow the static IP address to be configurable.
netsh interface ip set address name="Local Area Connection" ^
  static %HOSTONLYIP% %HOSTONLYMASK% %HOSTONLYGATEWAY% 1

if "%BRIDGED%" == "yes" (
    netsh interface ip set address name="Local Area Connection 2" ^
        static %BRIDGEDIP% %BRIDGEDMASK% %BRIDGEDGATEWAY% 1
)

echo Installing 3rd party software.
call C:\deps.bat

echo Initiate VM hardening.
C:\Python27\Python.exe C:\bootstrap.py

echo Cleaning up.
del C:\click.exe C:\deps.bat C:\bootstrap.py
del C:\settings.bat C:\settings.py
echo Y|rmdir /S C:\deps

start C:\Python27\Pythonw.exe C:\agent.py
