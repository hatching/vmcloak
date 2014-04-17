echo Installing Python
start C:\Python-2.7.6.msi
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Next >"
C:\click.exe "Python 2.7.6 Setup" "Finish"

echo Cleaning up
del C:\click.exe
del C:\Python-2.7.6.msi
del C:\Windows\System32\nLite.cmd

start C:\Python27\Python.exe C:\bootstrap.py
