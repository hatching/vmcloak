# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

config = """
INSTALL_SILENT=Enable
AUTO_UPDATE=Disable
EULA=Disable
SPONSORS=Disable
WEB_JAVA_SECURITY_LEVEL=H
WEB_ANALYTICS=Disable
"""

class Java(Dependency):
    name = "java"
    default = "7"
    exes = [
        # lots of java7 - http://www.oracle.com/technetwork/java/javase/downloads/java-archive-downloads-javase7-521261.html
        {
            "version": "7",
            "url": "http://cuckoo.sh/vmcloak/jdk-7-windows-i586.exe",
            "sha1": "2546a78b6138466b3e23e25b5ca59f1c89c22d03",
        },
        # lots of java8 - http://www.oracle.com/technetwork/java/javase/downloads/java-archive-javase8-2177648.html
        {
            "version": "8u101",
            "url": "http://cuckoo.sh/vmcloak/jdk-8u101-windows-i586.exe",
            "sha1": "2d2d56f5774cc2f15d9e54bebc9a868913e606b7",
        },
        {
            "version": "8u102",
            "url": "http://cuckoo.sh/vmcloak/jdk-8u102-windows-i586.exe",
            "sha1": "3acf0fca1d5bf56f8a2ce577d055bfd0dd1773f9",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\java.exe")
        
        if self.version.startswith("7"):
            self.a.execute("C:\\java.exe /s WEB_JAVA=1 WEB_JAVA_SECURITY_LEVEL=M SPONSORS=0", async=True)
        else:
            self.a.upload("C:\\config.cfg", config)
            self.a.execute("C:\\java.exe INSTALLCFG=C:\\config.cfg", async=True)
        
        # Wait until java.exe & javaw.exe are no longer running.
        self.wait_process_exit("java.exe")
        self.wait_process_exit("javaw.exe")

        self.a.remove("C:\\java.exe")
        
        if not self.version.startswith("7"):
            self.a.remove("C:\\config.cfg")

        if self.i.osversion == "winxp" or self.i.osversion == "win7x86":
            self.a.execute("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\JavaSoft\\Java Update\\Policy\" /v EnableJavaUpdate /t REG_DWORD /d 0 /f")

        if self.i.osversion == "win7x64":
            self.a.execute("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Wow6432Node\\JavaSoft\\Java Update\\Policy\" /v EnableJavaUpdate /t REG_DWORD /d 0 /f")

class Java7(Java, Dependency):
    """Backwards compatibility."""
    name = "java7"