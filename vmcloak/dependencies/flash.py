# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class Flash(Dependency):
    name = "flash"
    default = "11.7.700.169"
    recommended = True
    exes = [
        {
            "version": "11.4.402.287",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_4r402_287_winax.msi",
            "sha1": "99fb61ed221df9125698e78d659ee1fc93b97c60",
        },
        {
            "version": "11.6.602.168",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_6r602_168_winax.msi",
            "sha1": "906f920563403ace6dee9b0cff982ea02d4b5c06",
        },
        {
            "version": "11.7.700.169",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_7r700_169_winax.msi",
            "sha1": "790b09c63c44f0eafd7151096bf58964857d3b17",
        },
        {
            "version": "11.8.800.94",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_8r800_94_winax.msi",
            "sha1": "f7a152aa3af4a7bbef4f87ab5e05d24824ddf439",
        },
        {
            "version": "11.8.800.174",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_8r800_174_winax.msi",
            "sha1": "f3a466b33e11a72f3bef4ecd40ef63c19f97a077",
        },
        {
            "version": "11.9.900.117",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_9r900_117_winax.msi",
            "sha1": "982cf5626174e42814a7bb27ff62378b230dc201",
        },
        {
            "version": "11.9.900.170",
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_9r900_170_winax.msi",
            "sha1": "877c7e9a6de692bdef95a4f3cc22b9fb385db92e",
        },
        {
            "version": "12.0.0.38",
            "url": "https://cuckoo.sh/vmcloak/flashplayer12_0r0_38_winax.msi",
            "sha1": "e44908c9a813876c1a332a174b2e3e9dff47a4ff",
        },
        {
            "version": "13.0.0.182",
            "url": "https://cuckoo.sh/vmcloak/flashplayer13_0r0_182_winax.msi",
            "sha1": "fbe7a2698da29284be8366adaf8765e9990fd6e0",
        },
        {
            "version": "13.0.0.214",
            "url": "https://cuckoo.sh/vmcloak/flashplayer13_0r0_214_winax.msi",
            "sha1": "c79bfbb23b497cec805164df9f038644d74476aa",
        },
        {
            "version": "14.0.0.125",
            "url": "https://cuckoo.sh/vmcloak/flashplayer14_0r0_125_winax.msi",
            "sha1": "f6bd2b5e91195182898828cc1235fd27d2aa8d55",
        },
        {
            "version": "15.0.0.167",
            "url": "https://cuckoo.sh/vmcloak/flashplayer15_0r0_167_winax.msi",
            "sha1": "79f04ea94d033c07e7cc889751769e98f99d23fb",
        },
        {
            "version": "15.0.0.189",
            "url": "https://cuckoo.sh/vmcloak/flashplayer15_0r0_189_winax.msi",
            "sha1": "8bfd539853e0db0a58efdb8c5f5c021f1fcb9f8d",
        },
        {
            "version": "16.0.0.235",
            "url": "https://cuckoo.sh/vmcloak/flashplayer16_0r0_235_winax.msi",
            "sha1": "ad3da00825193ecee48440203b6051310f4de3b7",
        },
        {
            "version": "18.0.0.194",
            "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_194_winax.msi",
            "sha1": "2611f2d81ea8ef747f079d797099da89648566ed",
        },
        {
            "version": "18.0.0.203",
            "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_203_winax.msi",
            "sha1": "98ab0531be9f2b49adeb56c621678c17455e6f66",
        },
        {
            "version": "18.0.0.209",
            "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_209_winax.msi",
            "sha1": "a209b6a320965cfbd75455ee79ab28e03bd5371c",
        },
        {
            "version": "19.0.0.207",
            "url": "https://cuckoo.sh/vmcloak/flashplayer19_0r0_207_winax.msi",
            "sha1": "9a901f938add920ed846ae18187176cbdb40ecfb",
        },
        {
            "version": "19.0.0.245",
            "url": "https://cuckoo.sh/vmcloak/flashplayer19_0r0_245_winax.msi",
            "sha1": "1efef336190b021f6df3325f958f1698a91cce8c",
        },
        {
            "version": "20.0.0.228",
            "url": "https://cuckoo.sh/vmcloak/flashplayer20_0d0_228_winax.msi",
            "sha1": "fa86f107111fc7def35742097bf0aa29c82d7638",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\%s" % self.filename)
        self.a.execute("msiexec /i C:\\%s /passive" % self.filename)
        self.a.remove("C:\\%s" % self.filename)
