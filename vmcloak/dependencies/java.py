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
        {
            "version": "7u1",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u1-windows-i586.exe",
            "sha1": "ed434b8bc132a5bfda031428b26daf7b8331ecb9",
        },
        {
            "version": "7u2",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u2-windows-i586.exe",
            "sha1": "a36ae80b80dd1c9c5c466b3eb2451cd649613cfb",
        },
        {
            "version": "7u3",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u3-windows-i586.exe",
            "sha1": "fe9dc13c0a6424158dc0f13a6246a53973fb5369",
        },
        {
            "version": "7u4",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u4-windows-i586.exe",
            "sha1": "a2e927632b2106f5efefc906ed9070d8c0bf660f",
        },
        {
            "version": "7u5",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u5-windows-i586.exe",
            "sha1": "88c2fc5e5e61e7f709370c01abb138c65009307b",
        },
        {
            "version": "7u6",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u6-windows-i586.exe",
            "sha1": "09f3a1d0fe7fabd4cfdc1c23d1ed16016d064d01",
        },
        {
            "version": "7u7",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u7-windows-i586.exe",
            "sha1": "58e4bdd12225379284542b161e49d8eaea4e00c2",
        },
        {
            "version": "7u9",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u9-windows-i586.exe",
            "sha1": "11a256bd791033527580c6ac8700f3a72f7f4bcf",
        },
        {
            "version": "7u10",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u10-windows-i586.exe",
            "sha1": "f57bfa38a05433d902582fab9d08f530d7c7749b",
        },
        {
            "version": "7u11",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u11-windows-i586.exe",
            "sha1": "a482e48e151cff76dcc1479b9efc367da8fb66a7",
        },
        {
            "version": "7u13",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u13-windows-i586.exe",
            "sha1": "bd6848138385510b32897a5b04c94aa4cf2b4fca",
        },
        {
            "version": "7u15",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u15-windows-i586.exe",
            "sha1": "f52453c6fd665b89629e639abdb41492eff9a9e3",
        },
        {
            "version": "7u17",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u17-windows-i586.exe",
            "sha1": "1f462dea65c74dd9fdf094d852e438a0e6a036bc",
        },
        {
            "version": "7u21",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u21-windows-i586.exe",
            "sha1": "f677efa8309e99fe3a47ea09295b977af01f2142",
        },
        {
            "version": "7u25",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u25-windows-i586.exe",
            "sha1": "5eeb8869f9abcb8d575a7f75a6f85550edf680f5",
        },
        {
            "version": "7u40",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u40-windows-i586.exe",
            "sha1": "b611fb48bb5071b54ef45633cd796a27d5cd0ffd",
        },
        {
            "version": "7u45",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u45-windows-i586.exe",
            "sha1": "cfd7e00fa0f6b3eef32832dd7487c6f56e7f55b8",
        },
        {
            "version": "7u51",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u51-windows-i586.exe",
            "sha1": "439435a1b40053761e3a555e97befb4573c303e5",
        },
        {
            "version": "7u55",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u55-windows-i586.exe",
            "sha1": "bb244a96e58724415380877230d2f6b466e9e581",
        },
        {
            "version": "7u60",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u60-windows-i586.exe",
            "sha1": "8f9185b1fb80dee64e511e222c1a9742eff7837f",
        },
        {
            "version": "7u65",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u65-windows-i586.exe",
            "sha1": "9c52a8185b9931b8ae935adb63c8272cf6d9e9ba",
        },
        {
            "version": "7u67",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u67-windows-i586.exe",
            "sha1": "dff04608d4c045cdd66dffe726aed27b22939c9e",
        },
        {
            "version": "7u71",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u71-windows-i586.exe",
            "sha1": "8ca5c5ad43148dfc0e5640db114e317f1bbd6a25",
        },
        {
            "version": "7u72",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u72-windows-i586.exe",
            "sha1": "57f7dff98bdfbe064af159bbd1d8753cad714f68",
        },
        {
            "version": "7u75",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u75-windows-i586.exe",
            "sha1": "700e56c9b57f5349d4fe9ba28878973059dc68fa",
        },
        {
            "version": "7u76",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u76-windows-i586.exe",
            "sha1": "0469ba6302aa3dc03e39075451aef1c60e5e4114",
        },
        {
            "version": "7u79",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u79-windows-i586.exe",
            "sha1": "319306c148c97f404c00e5562b11f5f4ea5fd6e5",
        },
        {
            "version": "7u80",
            "url": "http://cuckoo.sh/vmcloak/jdk-7u80-windows-i586.exe",
            "sha1": "aebbc0b02c16e7169b0577962fa91c613f8a7a45",
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