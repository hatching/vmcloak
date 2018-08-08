# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Flash(Dependency):
    name = "flash"
    default = "11.7.700.169"
    recommended = True
    exes = [{
        "version": "11.4.402.287",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_4r402_287_winax.msi",
        "sha1": "99fb61ed221df9125698e78d659ee1fc93b97c60",
    }, {
        "version": "11.6.602.168",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_6r602_168_winax.msi",
        "sha1": "906f920563403ace6dee9b0cff982ea02d4b5c06",
    }, {
        # Released 4/9/2013
        "version": "11.7.700.169",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_7r700_169_winax.msi",
        "sha1": "790b09c63c44f0eafd7151096bf58964857d3b17",
    }, {
        "version": "11.8.800.94",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_8r800_94_winax.msi",
        "sha1": "f7a152aa3af4a7bbef4f87ab5e05d24824ddf439",
    }, {
        "version": "11.8.800.174",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_8r800_174_winax.msi",
        "sha1": "f3a466b33e11a72f3bef4ecd40ef63c19f97a077",
    }, {
        "version": "11.9.900.117",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_9r900_117_winax.msi",
        "sha1": "982cf5626174e42814a7bb27ff62378b230dc201",
    }, {
        "version": "11.9.900.170",
        "url": "https://cuckoo.sh/vmcloak/flashplayer11_9r900_170_winax.msi",
        "sha1": "877c7e9a6de692bdef95a4f3cc22b9fb385db92e",
    }, {
        # Released 1/14/2014
        "version": "12.0.0.38",
        "url": "https://cuckoo.sh/vmcloak/flashplayer12_0r0_38_winax.msi",
        "sha1": "e44908c9a813876c1a332a174b2e3e9dff47a4ff",
    }, {
        "version": "13.0.0.182",
        "url": "https://cuckoo.sh/vmcloak/flashplayer13_0r0_182_winax.msi",
        "sha1": "fbe7a2698da29284be8366adaf8765e9990fd6e0",
    }, {
        "version": "13.0.0.214",
        "url": "https://cuckoo.sh/vmcloak/flashplayer13_0r0_214_winax.msi",
        "sha1": "c79bfbb23b497cec805164df9f038644d74476aa",
    }, {
        "version": "14.0.0.125",
        "url": "https://cuckoo.sh/vmcloak/flashplayer14_0r0_125_winax.msi",
        "sha1": "f6bd2b5e91195182898828cc1235fd27d2aa8d55",
    }, {
        "version": "15.0.0.167",
        "url": "https://cuckoo.sh/vmcloak/flashplayer15_0r0_167_winax.msi",
        "sha1": "79f04ea94d033c07e7cc889751769e98f99d23fb",
    }, {
        "version": "15.0.0.189",
        "url": "https://cuckoo.sh/vmcloak/flashplayer15_0r0_189_winax.msi",
        "sha1": "8bfd539853e0db0a58efdb8c5f5c021f1fcb9f8d",
    }, {
        "version": "16.0.0.235",
        "url": "https://cuckoo.sh/vmcloak/flashplayer16_0r0_235_winax.msi",
        "sha1": "ad3da00825193ecee48440203b6051310f4de3b7",
    }, {
        "version": "18.0.0.194",
        "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_194_winax.msi",
        "sha1": "2611f2d81ea8ef747f079d797099da89648566ed",
    }, {
        "version": "18.0.0.203",
        "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_203_winax.msi",
        "sha1": "98ab0531be9f2b49adeb56c621678c17455e6f66",
    }, {
        "version": "18.0.0.209",
        "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_209_winax.msi",
        "sha1": "a209b6a320965cfbd75455ee79ab28e03bd5371c",
    }, {
        "version": "19.0.0.207",
        "url": "https://cuckoo.sh/vmcloak/flashplayer19_0r0_207_winax.msi",
        "sha1": "9a901f938add920ed846ae18187176cbdb40ecfb",
    }, {
        "version": "19.0.0.245",
        "url": "https://cuckoo.sh/vmcloak/flashplayer19_0r0_245_winax.msi",
        "sha1": "1efef336190b021f6df3325f958f1698a91cce8c",
    }, {
        # Released 12/8/2015
        "version": "20.0.0.228",
        "url": "https://cuckoo.sh/vmcloak/flashplayer20_0d0_228_winax.msi",
        "sha1": "fa86f107111fc7def35742097bf0aa29c82d7638",
    }, {
        # Released 1/19/2016
        "version": "20.0.0.286",
        "url": "https://cuckoo.sh/vmcloak/flashplayer20_0r0_286_winax.msi",
        "sha1": "a1b73c662b7bce03ff2d8a729005e81036ea1a24",
    }, {
        # Released 2/9/2016
        "version": "20.0.0.306",
        "url": "https://cuckoo.sh/vmcloak/flashplayer20_0r0_306_winax.msi",
        "sha1": "68ae4277d68146749cb6cf597d3d6be07422c372",
    }, {
        # Released 3/10/2016
        "version": "21.0.0.182",
        "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_182_winax.msi",
        "sha1": "717582fc7138c9cf4b3ec88413d38cddf8613d4c",
    }, {
        # Released 3/23/2016
        "version": "21.0.0.197",
        "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_197_winax.msi",
        "sha1": "1e81a4617abcbb95ee6bf9250be5a205ce0d289b",
    }, {
        # Released 4/7/2016
        "version": "21.0.0.213",
        "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_213_winax.msi",
        "sha1": "6d23ae1f12682b6baa1833c12955ca9adf7d13f2",
    }, {
        # Released 5/12/2016
        "version": "21.0.0.242",
        "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_242_winax.msi",
        "sha1": "01261660476cdcacf1872a8a5142018bce6de1dc",
    }, {
        # Released 6/16/2016
        "version": "22.0.0.192",
        "url": "https://cuckoo.sh/vmcloak/flashplayer22_0r0_192_winax.msi",
        "sha1": "6aba77bca04f7170ac90c3852b837027f840b051",
    }, {
        # Released 7/12/2016
        "version": "22.0.0.209",
        "url": "https://cuckoo.sh/vmcloak/flashplayer22_0r0_209_winax.msi",
        "sha1": "7db31a028cf14bdcdb4374fd941c08412130e384",
    }, {
        # Released 9/13/2016
        "version": "23.0.0.162",
        "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_162_winax.msi",
        "sha1": "4408e4b6c9ced6490d2b0b81d6a62d00776c8042",
    }, {
        # Released 10/11/2016
        "version": "23.0.0.185",
        "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_185_winax.msi",
        "sha1": "b86c4a79c445481992ac41c47a22323068ca40b1",
    }, {
        # Released 10/26/2016
        "version": "23.0.0.205",
        "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_205_winax.msi",
        "sha1": "c329a24860028263631411bd1c37369022473e9a",
    }, {
        # Released 11/8/2016
        "version": "23.0.0.207",
        "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_207_winax.msi",
        "sha1": "699097fa5bbc4d3a0a9733108678ee642d1cc667",
    }, {
        # Released 12/13/2016
        "version": "24.0.0.186",
        "url": "https://cuckoo.sh/vmcloak/flashplayer24_0r0_186_winax.msi",
        "sha1": "f9828b0e872f71879664078dbaa23b05fff47494",
    }, {
        # Released 1/10/2017
        "version": "24.0.0.194",
        "url": "https://cuckoo.sh/vmcloak/flashplayer24_0r0_194_winax.msi",
        "sha1": "2d9648adf6fdc05cbc61b037ec5e434c7a73dfe4",
    }, {
        # Released 2/14/2017
        "version": "24.0.0.221",
        "url": "https://cuckoo.sh/vmcloak/flashplayer24_0r0_221_winax.msi",
        "sha1": "e8ac1c9c4e12ce7164b1f7374e6ef2868ab51e7f",
    }, {
        # Released 03/14/2017
        "version": "25.0.0.127",
        "url": "https://cuckoo.sh/vmcloak/flashplayer25_0r0_127_winax.msi",
        "sha1": "78618c96a0e65cc1ace1aedb0ecac04972b3ac7f",
    }, {
        # Released 04/11/2017
        "version": "25.0.0.148",
        "url": "https://cuckoo.sh/vmcloak/flashplayer25_0r0_148_winax.msi",
        "sha1": "e3907d0e0ac26a2db556ee6fa864243f3cb0a9f0",
    }, {
        "version": "latest",
        "urls": [
            "https://fpdownload.macromedia.com/pub/flashplayer/latest/help/install_flash_player_ax.exe",
        ],
    }]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)

        if self.filename.endswith(".msi"):
            self.a.execute("msiexec /i C:\\%s /passive" % self.filename)
        else:
            self.a.execute("C:\\%s -install" % self.filename)

        mms = (
            "SilentAutoUpdateEnable=0\r\n"
            "AutoUpdateDisable=1\r\n"
            "ProtectedMode=0\r\n"
        )

        if self.h.arch == "x86":
            mmsfp = "C:\\Windows\\System32\\Macromed\\Flash\\mms.cfg"
        else:
            mmsfp = "C:\\Windows\\SysWow64\\Macromed\\Flash\\mms.cfg"

        self.a.upload(mmsfp, mms)
        self.a.remove("C:\\%s" % self.filename)
