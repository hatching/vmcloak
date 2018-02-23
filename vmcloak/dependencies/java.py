# Copyright (C) 2016-2018 Jurriaan Bremer.
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

java7deploymentconfig = """
deployment.system.config=file:///C:/Windows/Sun/Java/Deployment/deployment.properties
deployment.system.config.mandatory=true
"""

java7deploymentproperties = """
deployment.security.level=MEDIUM
deployment.security.level.locked
deployment.security.jsse.hostmismatch.warning=false
deployment.security.jsse.hostmismatch.warning.locked
deployment.security.mixcode=DISABLE
deployment.security.mixcode.locked
deployment.security.blacklist.check=false
deployment.security.blacklist.check.locked
deployment.security.sandbox.awtwarningwindow=false
deployment.security.sandbox.awtwarningwindow.locked
deployment.security.revocation.check=NO_CHECK
deployment.security.revocation.check.locked
deployment.javaws.shortcut=ALWAYS
deployment.javaws.shortcut.locked
deployment.webjava.enabled=true
deployment.webjava.enabled.locked
deployment.insecure.jres=NEVER
deployment.insecure.jres.locked
deployment.expiration.check.enabled=false
deployment.expiration.check.enabled.locked
"""

class Java(Dependency):
    name = "java"
    default = "jdk7"
    recommended = True
    exes = [{
    # http://www.oracle.com/technetwork/java/javase/downloads/java-archive-downloads-javase7-521261.html
    # https://www.java.com/pt_BR/download/manual.jsp
        "version": "jdk7",
        "url": "https://cuckoo.sh/vmcloak/jdk-7-windows-i586.exe",
        "sha1": "2546a78b6138466b3e23e25b5ca59f1c89c22d03",
    }, {
        "version": "7",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=50974",
        ],
        "sha1": "0faa00705651531c831380a6af83b564b995ecb0",
        "filename": "jre-7-windows-i586.exe",
    }, {
        "version": "jdk7u1",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u1-windows-i586.exe",
        "sha1": "ed434b8bc132a5bfda031428b26daf7b8331ecb9",
    }, {
        "arch": "x86",
        "version": "7u1",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=56868",
        ],
        "sha1": "26ec209d66c3b21ef3c7b6c1f3b9fa52466420ed",
        "filename": "jre-7u1-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u1",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=56869",
        ],
        "sha1": "bd40f1dcd72326bb472cd131acb04d707566e706",
        "filename": "jre-7u1-windows-x64.exe",
    }, {
        "version": "7u2",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u2-windows-i586.exe",
        "sha1": "a36ae80b80dd1c9c5c466b3eb2451cd649613cfb",
    }, {
        "version": "jdk7u3",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u3-windows-i586.exe",
        "sha1": "fe9dc13c0a6424158dc0f13a6246a53973fb5369",
    }, {
        "arch": "x86",
        "version": "7u3",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=60508",
        ],
        "sha1": "61f48fa0875c85acc8fe1476a1297212f96ea827",
        "filename": "jre-7u3-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u3",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=60509",
        ],
        "sha1": "0d74117467cd905f41fd807f7cdbaa671a150311",
        "filename": "jre-7u3-windows-x64.exe",
    }, {
        "version": "7u4",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u4-windows-i586.exe",
        "sha1": "a2e927632b2106f5efefc906ed9070d8c0bf660f",
    }, {
        "version": "jdk7u5",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u5-windows-i586.exe",
        "sha1": "88c2fc5e5e61e7f709370c01abb138c65009307b",
    }, {
        "arch": "x86",
        "version": "7u5",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=65692",
        ],
        "sha1": "504d94c7cc1617b44af8d81de6fd83120b04dfa5",
        "filename": "jre-7u5-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u5",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=65693",
        ],
        "sha1": "ca01de8bf2290c9b891c0bf4aac4c099f66d80e7",
        "filename": "jre-7u5-windows-x64.exe",
    }, {
        "version": "7u6",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u6-windows-i586.exe",
        "sha1": "09f3a1d0fe7fabd4cfdc1c23d1ed16016d064d01",
    }, {
        "version": "jdk7u7",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u7-windows-i586.exe",
        "sha1": "58e4bdd12225379284542b161e49d8eaea4e00c2",
    }, {
        "arch": "x86",
        "version": "7u7",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=68242",
        ],
        "sha1": "fad4496cd61a0ef1b42c27aeb405a3739ea0943f",
        "filename": "jre-7u7-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u7",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=68736",
        ],
        "sha1": "9af03460c416931bdee18c2dcebff5db50cb8cb3",
        "filename": "jre-7u7-windows-x64.exe",
    }, {
        "version": "jdk7u9",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u9-windows-i586.exe",
        "sha1": "11a256bd791033527580c6ac8700f3a72f7f4bcf",
    }, {
        "arch": "x86",
        "version": "7u9",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=69474",
        ],
        "sha1": "18c70915192bf5069543b8f95dd44f159ea6deec",
        "filename": "jre-7u9-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u9",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=69476",
        ],
        "sha1": "7ae6d07324439a203af612789110691f757b980e",
        "filename": "jre-7u9-windows-x64.exe",
    }, {
        "version": "jdk7u10",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u10-windows-i586.exe",
        "sha1": "f57bfa38a05433d902582fab9d08f530d7c7749b",
    }, {
        "arch": "x86",
        "version": "7u10",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=71835",
        ],
        "sha1": "d159c752086d6134aacb2e15a10ccaf8ef39bca0",
        "filename": "jre-7u10-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u10",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=71837",
        ],
        "sha1": "1c01773d0fd8e53af5fbf3cd2203ad6cf2545dbc",
        "filename": "jre-7u10-windows-x64.exe",
    }, {
        "version": "jdk7u11",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u11-windows-i586.exe",
        "sha1": "a482e48e151cff76dcc1479b9efc367da8fb66a7",
    }, {
        "arch": "x86",
        "version": "7u11",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=73141",
        ],
        "sha1": "682fb136563f08c20d37b25a28fce0883f893d8b",
        "filename": "jre-7u11-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u11",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=73143",
        ],
        "sha1": "41c3af2cf67c367066863a067ce831cf80586cdb",
        "filename": "jre-7u11-windows-x64.exe",
    }, {
        "version": "jdk7u13",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u13-windows-i586.exe",
        "sha1": "bd6848138385510b32897a5b04c94aa4cf2b4fca",
    }, {
        "arch": "x86",
        "version": "7u13",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=73857",
        ],
        "sha1": "72ad271c6c7e7d1893a9661aad2854a75e87cd5f",
        "filename": "jre-7u13-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u13",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=73859",
        ],
        "sha1": "0acc9b9d6a7f4ebd255c0cc720a6f452797c487f",
        "filename": "jre-7u13-windows-x64.exe",
    }, {
        "version": "jdk7u15",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u15-windows-i586.exe",
        "sha1": "f52453c6fd665b89629e639abdb41492eff9a9e3",
    }, {
        "arch": "x86",
        "version": "7u15",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=74781",
        ],
        "sha1": "5348714e363eb7df9ce5698cfcbb324e525cbd92",
        "filename": "jre-7u15-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u15",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=74783",
        ],
        "sha1": "53345cc82bee2a8ddce8dea26992f371e25f37cd",
        "filename": "jre-7u15-windows-x64.exe",
    }, {
        "version": "jdk7u17",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u17-windows-i586.exe",
        "sha1": "1f462dea65c74dd9fdf094d852e438a0e6a036bc",
    }, {
        "arch": "x86",
        "version": "7u17",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=75259",
        ],
        "sha1": "7b2cd00ec4c57396642afcc463e6d895772925a8",
        "filename": "jre-7u17-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u17",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=75261",
        ],
        "sha1": "eac554818507609480e8a890e232b3a8b0b2f55e",
        "filename": "jre-7u17-windows-x64.exe",
    }, {
        "version": "jdk7u21",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u21-windows-i586.exe",
        "sha1": "f677efa8309e99fe3a47ea09295b977af01f2142",
    }, {
        "arch": "x86",
        "version": "7u21",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=76860",
        ],
        "sha1": "620472dc1e7d015ed9a7700b846565a707946fcb",
        "filename": "jre-7u21-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u21",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=76862",
        ],
        "sha1": "9ec7523c5b8f5621ae21ab2fec12597ea029bb7f",
        "filename": "jre-7u21-windows-x64.exe",
    }, {
        "version": "jdk7u25",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u25-windows-i586.exe",
        "sha1": "5eeb8869f9abcb8d575a7f75a6f85550edf680f5",
    }, {
        "arch": "x86",
        "version": "7u25",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=78825",
        ],
        "sha1": "08ce588fb3668e987a0fa93becf754e9c8027d51",
        "filename": "jre-7u25-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u25",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=78827",
        ],
        "sha1": "ad65e982d8ebf03bb2ddbb418aa26ab499daee41",
        "filename": "jre-7u25-windows-x64.exe",
    }, {
        "version": "jdk7u40",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u40-windows-i586.exe",
        "sha1": "b611fb48bb5071b54ef45633cd796a27d5cd0ffd",
    }, {
        "arch": "x86",
        "version": "7u40",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=80812",
        ],
        "sha1": "c0429dca47c0f22bbcd33492f39117245bab515d",
        "filename": "jre-7u40-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u40",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=80814",
        ],
        "sha1": "85c7db9a1c432a119c90d1d1b203ccaaedae3444",
        "filename": "jre-7u40-windows-x64.exe",
    }, {
        "version": "jdk7u45",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u45-windows-i586.exe",
        "sha1": "cfd7e00fa0f6b3eef32832dd7487c6f56e7f55b8",
    }, {
        "arch": "x86",
        "version": "7u45",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=81819",
        ],
        "sha1": "a2269c804418186c9b944746f26e225b3e77a571",
        "filename": "jre-7u45-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u45",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=81821",
        ],
        "sha1": "155008d2cb8392befb4dcfec8afc5fd2c84173cc",
        "filename": "jre-7u45-windows-x64.exe",
    }, {
        "version": "jdk7u51",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u51-windows-i586.exe",
        "sha1": "439435a1b40053761e3a555e97befb4573c303e5",
    }, {
        "arch": "x86",
        "version": "7u51",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=83383",
        ],
        "sha1": "72aa32f97a0ddd306d436ac3f13fabb841b94a76",
        "filename": "jre-7u51-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u51",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=83385",
        ],
        "sha1": "0d3346f4c249d9443237205cc1c0dde1ef534874",
        "filename": "jre-7u51-windows-x64.exe",
    }, {
        "version": "jdk7u55",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u55-windows-i586.exe",
        "sha1": "bb244a96e58724415380877230d2f6b466e9e581",
    }, {
        "arch": "x86",
        "version": "7u55",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=86895",
        ],
        "sha1": "96b937f49f07068313530db491b92e7e9afb80ba",
        "filename": "jre-7u55-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u55",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=87443",
        ],
        "sha1": "567c3bc32254b2235f0bc30e910323e2dd1e38aa",
        "filename": "jre-7u55-windows-x64.exe",
    }, {
        "version": "jdk7u60",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u60-windows-i586.exe",
        "sha1": "8f9185b1fb80dee64e511e222c1a9742eff7837f",
    }, {
        "arch": "x86",
        "version": "7u60",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=90223",
        ],
        "sha1": "1672aed79505e52b6c39ee706d2f424910ad4493",
        "filename": "jre-7u60-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u60",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=90225",
        ],
        "sha1": "29162a9087b41a0fb2a476ebc78ae5d2ae02495a",
        "filename": "jre-7u60-windows-x64.exe",
    }, {
        "version": "jdk7u65",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u65-windows-i586.exe",
        "sha1": "9c52a8185b9931b8ae935adb63c8272cf6d9e9ba",
    }, {
        "arch": "x86",
        "version": "7u65",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=90223",
        ],
        "sha1": "0eb1db8fd71552ed48099881e2bde8bd41bbe53a",
        "filename": "jre-7u65-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u65",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=90225",
        ],
        "sha1": "8154af812e608bd0c8193c4d5e332a4133ed1aee",
        "filename": "jre-7u60-windows-x64.exe",
    }, {
        "version": "jdk7u67",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u67-windows-i586.exe",
        "sha1": "dff04608d4c045cdd66dffe726aed27b22939c9e",
    }, {
        "arch": "x86",
        "version": "7u67",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=95123",
        ],
        "sha1": "cdcb564088e565b3ed56d9bc9d80448a4e3a9fc6",
        "filename": "jre-7u67-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u67",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=95125",
        ],
        "sha1": "7d9413d367faa0b096ee72c2d5f1983bb7334e9e",
        "filename": "jre-7u67-windows-x64.exe",
    }, {
        "version": "jdk7u71",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u71-windows-i586.exe",
        "sha1": "8ca5c5ad43148dfc0e5640db114e317f1bbd6a25",
    }, {
        "arch": "x86",
        "version": "7u71",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=97807",
        ],
        "sha1": "b04ba06f787b596c57ede7e3c0250546d0635f73",
        "filename": "jre-7u71-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u71",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=97809",
        ],
        "sha1": "714240cf53190bfccb0bb237323a2496300be946",
        "filename": "jre-7u71-windows-x64.exe",
    }, {
        "version": "7u72",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u72-windows-i586.exe",
        "sha1": "57f7dff98bdfbe064af159bbd1d8753cad714f68",
    }, {
        "version": "jdk7u75",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u75-windows-i586.exe",
        "sha1": "700e56c9b57f5349d4fe9ba28878973059dc68fa",
    }, {
        "arch": "x86",
        "version": "7u75",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=101467",
        ],
        "sha1": "cd5f2222c6a9db6adfb385eaaeff8f95ea32446f",
        "filename": "jre-7u75-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u75",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=101469",
        ],
        "sha1": "488492de778fc47f67a33c65ea922124279c20d4",
        "filename": "jre-7u75-windows-x64.exe",
    }, {
        "version": "7u76",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u76-windows-i586.exe",
        "sha1": "0469ba6302aa3dc03e39075451aef1c60e5e4114",
    }, {
        "version": "jdk7u79",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u79-windows-i586.exe",
        "sha1": "319306c148c97f404c00e5562b11f5f4ea5fd6e5",
    }, {
        "arch": "x86",
        "version": "7u79",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=106367",
        ],
        "sha1": "b062b03a04e0f3ce222282ca1760e4234d3c6f1f",
        "filename": "jre-7u79-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "7u79",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=106369",
        ],
        "sha1": "6e407b926eaf023e4248fdfffa810ded9d4ac7a3",
        "filename": "jre-7u79-windows-x64.exe",
    }, {
        "version": "7u80",
        "url": "https://cuckoo.sh/vmcloak/jdk-7u80-windows-i586.exe",
        "sha1": "aebbc0b02c16e7169b0577962fa91c613f8a7a45",
    }, {
        # http://www.oracle.com/technetwork/java/javase/downloads/java-archive-javase8-2177648.html
        "version": "8",
        "url": "https://cuckoo.sh/vmcloak/jdk-8-windows-i586.exe",
        "sha1": "09a05b1afad97ffa35a47d571752c3e804c200c7",
    }, {
        "version": "jdk8u5",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u5-windows-i586.exe",
        "sha1": "81660732a53e08651c633d99b0e6042cbbaf616d",
    }, {
        "arch": "x86",
        "version": "8u5",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=86957",
        ],
        "sha1": "ca48401f6f71ad360b3c0882393e2c93c35f80de",
        "filename": "jre-8u5-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u5",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=86958",
        ],
        "sha1": "ca656e8a722c068939665ad23760b8b072281594",
        "filename": "jre-8u5-windows-x64.exe",
    }, {
        "version": "8u11",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u11-windows-i586.exe",
        "sha1": "757103707b16e6a79ebd4d134613e483007a0c7a",
    }, {
        "version": "8u20",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u20-windows-i586.exe",
        "sha1": "30df3349f710e6b54adccadadc1e1f939ab2f6da",
    }, {
        "version": "jdk8u25",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u25-windows-i586.exe",
        "sha1": "79b4b68aea5ef6448c39c2ee3103722db6548ff0",
    }, {
        "arch": "x86",
        "version": "8u25",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=98426",
        ],
        "sha1": "ff3d21c97e9ca71157f12221ccf0788a9775ec92",
        "filename": "jre-8u25-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u25",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=98428",
        ],
        "sha1": "73024362b55d35f77562f203faba892c7540b68d",
        "filename": "jre-8u25-windows-x64.exe",
    }, {
        "version": "jdk8u31",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u31-windows-i586.exe",
        "sha1": "5b8a1f8d11ecbcd46ed3389498ef67a4f699133b",
    }, {
        "arch": "x86",
        "version": "8u31",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=101406",
        ],
        "sha1": "b8ef84ba6a68c35b5d7a5304b4c0304aa53858b8",
        "filename": "jre-8u31-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u31",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=101408",
        ],
        "sha1": "00b5d23743d097d9b8f50bd14602bf4bae525b00",
        "filename": "jre-8u31-windows-x64.exe",
    }, {
        "version": "jdk8u40",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u40-windows-i586.exe",
        "sha1": "ff9f4d62dffa0a81abbc0e5e151586301ddf4884",
    }, {
        "arch": "x86",
        "version": "8u40",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=103426",
        ],
        "sha1": "c583ea81fe3cf6b06e2851f6805ec895226a0053",
        "filename": "jre-8u40-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u40",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=103428",
        ],
        "sha1": "3034ee9474c8829cb9145f3ceadf4e4f8618b9f8",
        "filename": "jre-8u40-windows-x64.exe",
    }, {
        "version": "jdk8u45",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u45-windows-i586.exe",
        "sha1": "8e839fe0e30a56784566017f6acdb0fbe213c8bc",
    }, {
        "arch": "x86",
        "version": "8u45",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=106246",
        ],
        "sha1": "7fc89bd7f82a092d2aa15b753f1fa17e47b879aa",
        "filename": "jre-8u45-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u45",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=106248",
        ],
        "sha1": "4d71c0fccdad64149da2edbd89b8871c83ad5f7e",
        "filename": "jre-8u45-windows-x64.exe",
    }, {
        "version": "jdk8u51",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u51-windows-i586.exe",
        "sha1": "0aaee8ff5f62fdcb3685d513be471c49824d7e04",
    }, {
        "arch": "x86",
        "version": "8u51",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=107943",
        ],
        "sha1": "e0e42aaeedbb77a19809004a576496dcdcf99ed5",
        "filename": "jre-8u51-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u51",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=107944",
        ],
        "sha1": "447fd1f59219282ec5d2f7a179ac12cc072171c3",
        "filename": "jre-8u51-windows-x64.exe",
    }, {
        "version": "jdk8u60",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u60-windows-i586.exe",
        "sha1": "47b36bc0fdc44029f82a50346fbb85b8f7803d7f",
    }, {
        "arch": "x86",
        "version": "8u60",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=109706",
        ],
        "sha1": "bd486f62bc358b1180218480a1cbb0a42483af98",
        "filename": "jre-8u60-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u60",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=109708",
        ],
        "sha1": "87976e29f58276685c63833ae42df7b2b5fe921c",
        "filename": "jre-8u60-windows-x64.exe",
    }, {
        "version": "jdk8u65",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u65-windows-i586.exe",
        "sha1": "66bdacc1252f309f157fd0786d2e148dbb394629",
    }, {
        "arch": "x86",
        "version": "8u65",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=111687",
        ],
        "sha1": "5e0b4ef55faf1de9b4b85d769bfe0899481c5d79",
        "filename": "jre-8u65-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u65",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=111689",
        ],
        "sha1": "85a8021af3299e5bc439a071e8b2cea6a137c6ad",
        "filename": "jre-8u65-windows-x64.exe",
    }, {
        "version": "jdk8u66",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u66-windows-i586.exe",
        "sha1": "0013f600723a1a16aa97f7c3fbe1c27fd7674cbe",
    }, {
        "arch": "x86",
        "version": "8u66",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=113217",
        ],
        "sha1": "b35523fe8891f4f29942482b0b9a205801294595",
        "filename": "jre-8u66-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u66",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=113219",
        ],
        "sha1": "b5a1871e28ab78aa0d48f0d61b3e03e98db50510",
        "filename": "jre-8u66-windows-x64.exe",
    }, {
        "version": "jdk8u71",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u71-windows-i586.exe",
        "sha1": "c6726fb46cb40b42b4b545502ee87172b7d290f5",
    }, {
        "arch": "x86",
        "version": "8u71",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=114687",
        ],
        "sha1": "42db2fbd719a173f6d6d81bbb05f4033628c798c",
        "filename": "jre-8u71-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u71",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=114689",
        ],
        "sha1": "7875f835edf7383b221ca7a4f6b81072727f6eed",
        "filename": "jre-8u71-windows-x64.exe",
    }, {
        "version": "8u72",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u72-windows-i586.exe",
        "sha1": "d1b6e793c21f1bec935f647ec49a12bc54109ace",
    }, {
        "version": "jdk8u73",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u73-windows-i586.exe",
        "sha1": "f56e21ece567f42fce5a38961bd81288dd2956c0",
    }, {
        "arch": "x86",
        "version": "8u73",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=116028",
        ],
        "sha1": "77551adf49d25bcbd3f9217190a87df8aef12b8a",
        "filename": "jre-8u73-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u73",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=116030",
        ],
        "sha1": "12c3e70c4348ba89e3817a5b48a41b26b1245550",
        "filename": "jre-8u73-windows-x64.exe",
    }, {
        "version": "8u74",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u74-windows-i586.exe",
        "sha1": "8fa2c7f22b9176d0201d40dc21c29bc7002f5251",
    }, {
        "version": "jdk8u77",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u77-windows-i586.exe",
        "sha1": "1560add14dde3e4c5bac020116f5bc06d49be567",
    }, {
        "arch": "x86",
        "version": "8u77",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=207229",
        ],
        "sha1": "c8a7641fb59e5a92118d6875c2598017852a89b1",
        "filename": "jre-8u77-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u77",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=207231",
        ],
        "sha1": "bba6259c407aef6fb746140965d7285911c42ce1",
        "filename": "jre-8u77-windows-x64.exe",
    }, {
        "version": "jdk8u91",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u91-windows-i586.exe",
        "sha1": "5374b68f6cca15345fd7d8de0b352cd37804068d",
    }, {
        "arch": "x86",
        "version": "8u91",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=207773",
        ],
        "sha1": "917463bf8712a0f2ec17704fe7170c735088a915",
        "filename": "jre-8u91-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u91",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=207775",
        ],
        "sha1": "1b7710217149ff0981949c77aa8aa4cbc5597991",
        "filename": "jre-8u91-windows-x64.exe",
    }, {
        "version": "8u92",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u92-windows-i586.exe",
        "sha1": "b89aa89d66ea1783628f62487a137c993af7ca8b",
    }, {
        "version": "jdk8u101",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u101-windows-i586.exe",
        "sha1": "2d2d56f5774cc2f15d9e54bebc9a868913e606b7",
    }, {
        "arch": "x86",
        "version": "8u101",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=211997",
        ],
        "sha1": "ae3ad283a4a175a3b5e1e143330ce194b7ebe560",
        "filename": "jre-8u101-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u101",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=211999",
        ],
        "sha1": "cb8404bafad323694d7aa622f02d466073c61c2d",
        "filename": "jre-8u101-windows-x64.exe",
    }, {
        "version": "8u102",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u102-windows-i586.exe",
        "sha1": "3acf0fca1d5bf56f8a2ce577d055bfd0dd1773f9",
    }, {
        "arch": "x86",
        "version": "8u111",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=216432",
        ],
        "sha1": "11d6a333a6d1b939a4d40082a4acab737071a7b8",
        "filename": "jre-8u111-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u111",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=216434",
        ],
        "sha1": "12e9492f2f2066f5b9187ed00995ede95491c445",
        "filename": "jre-8u111-windows-x64.exe",
    }, {
        "version": "jdk8u121",
        "url": "https://cuckoo.sh/vmcloak/jdk-8u121-windows-i586.exe",
        "sha1": "e71fc3eb9f895eba5c2836b05d627884edd0157a",
    }, {
        "arch": "x86",
        "version": "8u121",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=218831_e9e7ea248e2c4826b92b3f075a80e441",
        ],
        "sha1": "22ae33babe447fb28789bce713a20cbee796a37c",
        "filename": "jre-8u121-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u121",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=218833_e9e7ea248e2c4826b92b3f075a80e441",
        ],
        "sha1": "8b22c68147ba96a8ac6e18360ff2739a1c6ca1db",
        "filename": "jre-8u121-windows-x64.exe",
    }, {
        "arch": "x86",
        "version": "8u131",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=220313_d54c1d3a095b4ff2b6607d096fa80163",
        ],
        "sha1": "62762159368ea5fa7681913d2de3633c0d77ad2e",
        "filename": "jre-8u131-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u131",
        "urls": [
            "http://javadl.sun.com/webapps/download/AutoDL?BundleId=220315_d54c1d3a095b4ff2b6607d096fa80163",
        ],
        "sha1": "a3a75ebdab5079aac1b3c2f2a4666296214f0417",
        "filename": "jre-8u131-windows-x64.exe",
    }, {
        "arch": "x86",
        "version": "8u141",
        "urls": [
            "http://javadl.oracle.com/webapps/download/AutoDL?BundleId=224927_336fa29ff2bb4ef291e347e091f7f4a7",
        ],
        "sha1": "74445e1c2c932f87ad90a55fb5da182f57dd637d",
        "filename": "jre-8u141-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u141",
        "urls": [
            "http://javadl.oracle.com/webapps/download/AutoDL?BundleId=224929_336fa29ff2bb4ef291e347e091f7f4a7",
        ],
        "sha1": "77cfba433ca2057e6aef6ac1f82f3a3679bf8533",
        "filename": "jre-8u141-windows-x64.exe",
    }, {
        "arch": "x86",
        "version": "8u144",
        "urls": [
            "http://javadl.oracle.com/webapps/download/AutoDL?BundleId=225353_090f390dda5b47b9b721c7dfaa008135",
        ],
        "sha1": "49901a5961c2cdd9a46930d4008a8f8d0b1aad27",
        "filename": "jre-8u144-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u144",
        "urls": [
            "http://javadl.oracle.com/webapps/download/AutoDL?BundleId=225355_090f390dda5b47b9b721c7dfaa008135",
        ],
        "sha1": "f1c74179507212cd853a87fa3b6a9ea764dea4ed",
        "filename": "jre-8u144-windows-x64.exe",
    }, {
        "arch": "x86",
        "version": "8u151",
        "urls": [
            "http://javadl.oracle.com/webapps/download/AutoDL?BundleId=227550_e758a0de34e24606bca991d704f6dcbf",
        ],
        "sha1": "94f6903ef5514405131298fc351af9467adf945d",
        "filename": "jre-8u151-windows-i586.exe",
    }, {
        "arch": "amd64",
        "version": "8u151",
        "urls": [
            "http://javadl.oracle.com/webapps/download/AutoDL?BundleId=227552_e758a0de34e24606bca991d704f6dcbf",
        ],
        "sha1": "57747ce996b5b2f1786601b04a0b0355fc82493a",
        "filename": "jre-8u151-windows-x64.exe",
    }]

    def run(self):
        self.upload_dependency("C:\\java.exe")

        version = self.version.strip("jdk")

        if version.startswith("7"):
            self.a.upload("C:\\Windows\\Sun\\Java\\Deployment\\deployment.config", java7deploymentconfig)
            self.a.upload("C:\\Windows\\Sun\\Java\\Deployment\\deployment.properties", java7deploymentproperties)
            self.a.execute("C:\\java.exe /s", async=True)
        else:
            self.a.upload("C:\\config.cfg", config)
            self.a.execute("C:\\java.exe INSTALLCFG=C:\\config.cfg", async=True)

        # Wait until java.exe & javaw.exe are no longer running.
        self.wait_process_exit("java.exe")
        self.wait_process_exit("javaw.exe")

        self.a.remove("C:\\java.exe")

        if not version.startswith("7"):
            self.a.remove("C:\\config.cfg")

        if self.i.osversion == "winxp" or self.i.osversion == "win7x86":
            self.a.execute("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\JavaSoft\\Java Update\\Policy\" /v EnableJavaUpdate /t REG_DWORD /d 0 /f")

        if self.i.osversion == "win7x64":
            self.a.execute("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Wow6432Node\\JavaSoft\\Java Update\\Policy\" /v EnableJavaUpdate /t REG_DWORD /d 0 /f")

class Java7(Java, Dependency):
    """Backwards compatibility."""
    name = "java7"
    recommended = False
