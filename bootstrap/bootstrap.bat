call C:\settings.bat

echo Setting static IP address.
rem TODO Allow the static IP address to be configurable.
netsh interface ip set address name="Local Area Connection" ^
  static %HOSTONLYIP% 255.255.255.0 %HOSTONLYGATEWAY% 1

echo Installing 3rd party software.
call C:\dependencies.bat

echo Initiate VM hardening.
C:\Python27\Python.exe C:\bootstrap.py

echo Cleaning up.
del C:\click.exe C:\dependencies.bat C:\bootstrap.py
del C:\settings.bat C:\settings.py
echo Y|rmdir /S C:\dependencies

start C:\Python27\Pythonw.exe C:\agent.py
