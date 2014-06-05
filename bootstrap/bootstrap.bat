echo Installing Python.
start C:\Python-2.7.6.msi
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Finish"

echo Cleaning up.
del C:\click.exe
del C:\Python-2.7.6.msi
del C:\Windows\System32\nLite.cmd

echo Setting static IP address.
rem TODO Allow the static IP address to be configurable.
netsh interface ip set address name="Local Area Connection" ^
  static 192.168.56.101 255.255.255.0 192.168.0.1 1

C:\Python27\Pythonw.exe C:\bootstrap.py
start C:\Python27\Pythonw.exe C:\agent.py
