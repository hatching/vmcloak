# Copyright (C) 2014-2017 Jurriaan Bremer.
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
    recommended = True
    exes = [
        # http://www.oracle.com/technetwork/java/javase/downloads/java-archive-downloads-javase7-521261.html
        {
            "version": "7",
            "url": "https://cuckoo.sh/vmcloak/jdk-7-windows-i586.exe",
            "sha1": "2546a78b6138466b3e23e25b5ca59f1c89c22d03",
        },
        {
            "version": "7u1",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u1-windows-i586.exe",
            "sha1": "ed434b8bc132a5bfda031428b26daf7b8331ecb9",
        },
        {
            "version": "7u2",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u2-windows-i586.exe",
            "sha1": "a36ae80b80dd1c9c5c466b3eb2451cd649613cfb",
        },
        {
            "version": "7u3",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u3-windows-i586.exe",
            "sha1": "fe9dc13c0a6424158dc0f13a6246a53973fb5369",
        },
        {
            "version": "7u4",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u4-windows-i586.exe",
            "sha1": "a2e927632b2106f5efefc906ed9070d8c0bf660f",
        },
        {
            "version": "7u5",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u5-windows-i586.exe",
            "sha1": "88c2fc5e5e61e7f709370c01abb138c65009307b",
        },
        {
            "version": "7u6",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u6-windows-i586.exe",
            "sha1": "09f3a1d0fe7fabd4cfdc1c23d1ed16016d064d01",
        },
        {
            "version": "7u7",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u7-windows-i586.exe",
            "sha1": "58e4bdd12225379284542b161e49d8eaea4e00c2",
        },
        {
            "version": "7u9",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u9-windows-i586.exe",
            "sha1": "11a256bd791033527580c6ac8700f3a72f7f4bcf",
        },
        {
            "version": "7u10",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u10-windows-i586.exe",
            "sha1": "f57bfa38a05433d902582fab9d08f530d7c7749b",
        },
        {
            "version": "7u11",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u11-windows-i586.exe",
            "sha1": "a482e48e151cff76dcc1479b9efc367da8fb66a7",
        },
        {
            "version": "7u13",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u13-windows-i586.exe",
            "sha1": "bd6848138385510b32897a5b04c94aa4cf2b4fca",
        },
        {
            "version": "7u15",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u15-windows-i586.exe",
            "sha1": "f52453c6fd665b89629e639abdb41492eff9a9e3",
        },
        {
            "version": "7u17",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u17-windows-i586.exe",
            "sha1": "1f462dea65c74dd9fdf094d852e438a0e6a036bc",
        },
        {
            "version": "7u21",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u21-windows-i586.exe",
            "sha1": "f677efa8309e99fe3a47ea09295b977af01f2142",
        },
        {
            "version": "7u25",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u25-windows-i586.exe",
            "sha1": "5eeb8869f9abcb8d575a7f75a6f85550edf680f5",
        },
        {
            "version": "7u40",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u40-windows-i586.exe",
            "sha1": "b611fb48bb5071b54ef45633cd796a27d5cd0ffd",
        },
        {
            "version": "7u45",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u45-windows-i586.exe",
            "sha1": "cfd7e00fa0f6b3eef32832dd7487c6f56e7f55b8",
        },
        {
            "version": "7u51",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u51-windows-i586.exe",
            "sha1": "439435a1b40053761e3a555e97befb4573c303e5",
        },
        {
            "version": "7u55",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u55-windows-i586.exe",
            "sha1": "bb244a96e58724415380877230d2f6b466e9e581",
        },
        {
            "version": "7u60",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u60-windows-i586.exe",
            "sha1": "8f9185b1fb80dee64e511e222c1a9742eff7837f",
        },
        {
            "version": "7u65",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u65-windows-i586.exe",
            "sha1": "9c52a8185b9931b8ae935adb63c8272cf6d9e9ba",
        },
        {
            "version": "7u67",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u67-windows-i586.exe",
            "sha1": "dff04608d4c045cdd66dffe726aed27b22939c9e",
        },
        {
            "version": "7u71",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u71-windows-i586.exe",
            "sha1": "8ca5c5ad43148dfc0e5640db114e317f1bbd6a25",
        },
        {
            "version": "7u72",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u72-windows-i586.exe",
            "sha1": "57f7dff98bdfbe064af159bbd1d8753cad714f68",
        },
        {
            "version": "7u75",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u75-windows-i586.exe",
            "sha1": "700e56c9b57f5349d4fe9ba28878973059dc68fa",
        },
        {
            "version": "7u76",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u76-windows-i586.exe",
            "sha1": "0469ba6302aa3dc03e39075451aef1c60e5e4114",
        },
        {
            "version": "7u79",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u79-windows-i586.exe",
            "sha1": "319306c148c97f404c00e5562b11f5f4ea5fd6e5",
        },
        {
            "version": "7u80",
            "url": "https://cuckoo.sh/vmcloak/jdk-7u80-windows-i586.exe",
            "sha1": "aebbc0b02c16e7169b0577962fa91c613f8a7a45",
        },
        # http://www.oracle.com/technetwork/java/javase/downloads/java-archive-javase8-2177648.html
        {
            "version": "8",
            "url": "https://cuckoo.sh/vmcloak/jdk-8-windows-i586.exe",
            "sha1": "09a05b1afad97ffa35a47d571752c3e804c200c7",
        },
        {
            "version": "8u5",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u5-windows-i586.exe",
            "sha1": "81660732a53e08651c633d99b0e6042cbbaf616d",
        },
        {
            "version": "8u11",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u11-windows-i586.exe",
            "sha1": "757103707b16e6a79ebd4d134613e483007a0c7a",
        },
        {
            "version": "8u20",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u20-windows-i586.exe",
            "sha1": "30df3349f710e6b54adccadadc1e1f939ab2f6da",
        },
        {
            "version": "8u25",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u25-windows-i586.exe",
            "sha1": "79b4b68aea5ef6448c39c2ee3103722db6548ff0",
        },
        {
            "version": "8u31",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u31-windows-i586.exe",
            "sha1": "5b8a1f8d11ecbcd46ed3389498ef67a4f699133b",
        },
        {
            "version": "8u40",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u40-windows-i586.exe",
            "sha1": "ff9f4d62dffa0a81abbc0e5e151586301ddf4884",
        },
        {
            "version": "8u45",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u45-windows-i586.exe",
            "sha1": "8e839fe0e30a56784566017f6acdb0fbe213c8bc",
        },
        {
            "version": "8u51",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u51-windows-i586.exe",
            "sha1": "0aaee8ff5f62fdcb3685d513be471c49824d7e04",
        },
        {
            "version": "8u60",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u60-windows-i586.exe",
            "sha1": "47b36bc0fdc44029f82a50346fbb85b8f7803d7f",
        },
        {
            "version": "8u65",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u65-windows-i586.exe",
            "sha1": "66bdacc1252f309f157fd0786d2e148dbb394629",
        },
        {
            "version": "8u66",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u66-windows-i586.exe",
            "sha1": "0013f600723a1a16aa97f7c3fbe1c27fd7674cbe",
        },
        {
            "version": "8u71",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u71-windows-i586.exe",
            "sha1": "c6726fb46cb40b42b4b545502ee87172b7d290f5",
        },
        {
            "version": "8u72",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u72-windows-i586.exe",
            "sha1": "d1b6e793c21f1bec935f647ec49a12bc54109ace",
        },
        {
            "version": "8u73",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u73-windows-i586.exe",
            "sha1": "f56e21ece567f42fce5a38961bd81288dd2956c0",
        },
        {
            "version": "8u74",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u74-windows-i586.exe",
            "sha1": "8fa2c7f22b9176d0201d40dc21c29bc7002f5251",
        },
        {
            "version": "8u77",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u77-windows-i586.exe",
            "sha1": "1560add14dde3e4c5bac020116f5bc06d49be567",
        },
        {
            "version": "8u91",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u91-windows-i586.exe",
            "sha1": "5374b68f6cca15345fd7d8de0b352cd37804068d",
        },
        {
            "version": "8u92",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u92-windows-i586.exe",
            "sha1": "b89aa89d66ea1783628f62487a137c993af7ca8b",
        },
        {
            "version": "8u101",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u101-windows-i586.exe",
            "sha1": "2d2d56f5774cc2f15d9e54bebc9a868913e606b7",
        },
        {
            "version": "8u102",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u102-windows-i586.exe",
            "sha1": "3acf0fca1d5bf56f8a2ce577d055bfd0dd1773f9",
        },
        {
            "version": "8u121",
            "url": "https://cuckoo.sh/vmcloak/jdk-8u121-windows-i586.exe",
            "sha1": "e71fc3eb9f895eba5c2836b05d627884edd0157a",
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
    recommended = False
