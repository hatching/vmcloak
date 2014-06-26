call C:\settings.bat

echo Installing Python.
start C:\Python-2.7.6.msi
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Finish"

echo Setting static IP address.
rem TODO Allow the static IP address to be configurable.
netsh interface ip set address name="Local Area Connection" ^
  static %HOSTONLYIP% 255.255.255.0 %HOSTONLYGATEWAY% 1

echo Installing 3rd party software.
call C:\dependencies.bat

echo Initiate VM hardening.
C:\Python27\Python.exe C:\bootstrap.py

echo Cleaning up.
del C:\click.exe C:\Python-2.7.6.msi
del C:\bootstrap.py C:\settings.bat C:\settings.py
del C:\dependencies.bat
echo Y|rmdir /S C:\dependencies

start C:\Python27\Pythonw.exe C:\agent.py
