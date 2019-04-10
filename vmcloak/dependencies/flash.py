# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency


class Flash(Dependency):
    name = "flash"
    default = "11.7.700.169"
    recommended = True
    exes = [
        {
            # Released 10/8/2012
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_4r402_287_winax.msi",
            "version": "11.4.402.287",
            "sha1": "99fb61ed221df9125698e78d659ee1fc93b97c60"
        },
        {
            # Released 02/12/2013
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_6r602_168_winax.msi",
            "version": "11.6.602.168",
            "sha1": "906f920563403ace6dee9b0cff982ea02d4b5c06"
        },
        {
            # Released 4/9/2013
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_7r700_169_winax.msi",
            "version": "11.7.700.169",
            "sha1": "790b09c63c44f0eafd7151096bf58964857d3b17"
        },
        {
            # Released  7/9/2013
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_8r800_94_winax.msi",
            "version": "11.8.800.94",
            "sha1": "f7a152aa3af4a7bbef4f87ab5e05d24824ddf439"
        },
        {
            # Released 9/13/2013
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_8r800_174_winax.msi",
            "version": "11.8.800.174",
            "sha1": "f3a466b33e11a72f3bef4ecd40ef63c19f97a077"
        },
        {
            # Released 10/8/2013
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_9r900_117_winax.msi",
            "version": "11.9.900.117",
            "sha1": "982cf5626174e42814a7bb27ff62378b230dc201"
        },
        {
            # Released 12/10/2013
            "url": "https://cuckoo.sh/vmcloak/flashplayer11_9r900_170_winax.msi",
            "version": "11.9.900.170",
            "sha1": "877c7e9a6de692bdef95a4f3cc22b9fb385db92e"
        },
        {
            # Released 1/14/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer12_0r0_38_winax.msi",
            "version": "12.0.0.38",
            "sha1": "e44908c9a813876c1a332a174b2e3e9dff47a4ff"
        },
        {
            # Released 4/8/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer13_0r0_182_winax.msi",
            "version": "13.0.0.182",
            "sha1": "fbe7a2698da29284be8366adaf8765e9990fd6e0"
        },
        {
            # Released 5/13/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer13_0r0_214_winax.msi",
            "version": "13.0.0.214",
            "sha1": "c79bfbb23b497cec805164df9f038644d74476aa"
        },
        {
            # Released 6/10/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer14_0r0_125_winax.msi",
            "version": "14.0.0.125",
            "sha1": "f6bd2b5e91195182898828cc1235fd27d2aa8d55"
        },
        {
            # Released 9/9/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer15_0r0_167_winax.msi",
            "version": "15.0.0.167",
            "sha1": "79f04ea94d033c07e7cc889751769e98f99d23fb"
        },
        {
            # Released 10/14/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer15_0r0_189_winax.msi",
            "version": "15.0.0.189",
            "sha1": "8bfd539853e0db0a58efdb8c5f5c021f1fcb9f8d"
        },
        {
            # Released 12/9/2014
            "url": "https://cuckoo.sh/vmcloak/flashplayer16_0r0_235_winax.msi",
            "version": "16.0.0.235",
            "sha1": "ad3da00825193ecee48440203b6051310f4de3b7"
        },
        {
            # Released 6/23/2015
            "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_194_winax.msi",
            "version": "18.0.0.194",
            "sha1": "2611f2d81ea8ef747f079d797099da89648566ed"
        },
        {
            # Released 7/8/2015
            "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_203_winax.msi",
            "version": "18.0.0.203",
            "sha1": "98ab0531be9f2b49adeb56c621678c17455e6f66"
        },
        {
            # Released 7/14/2015
            "url": "https://cuckoo.sh/vmcloak/flashplayer18_0r0_209_winax.msi",
            "version": "18.0.0.209",
            "sha1": "a209b6a320965cfbd75455ee79ab28e03bd5371c"
        },
        {
            # Released 10/13/2015
            "url": "https://cuckoo.sh/vmcloak/flashplayer19_0r0_207_winax.msi",
            "version": "19.0.0.207",
            "sha1": "9a901f938add920ed846ae18187176cbdb40ecfb"
        },
        {
            # Released 11/10/2015
            "url": "https://cuckoo.sh/vmcloak/flashplayer19_0r0_245_winax.msi",
            "version": "19.0.0.245",
            "sha1": "1efef336190b021f6df3325f958f1698a91cce8c"
        },
        {
            # Released 12/8/2015
            "url": "https://cuckoo.sh/vmcloak/flashplayer20_0d0_228_winax.msi",
            "version": "20.0.0.228",
            "sha1": "fa86f107111fc7def35742097bf0aa29c82d7638"
        },
        {
            # Released 1/19/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer20_0r0_286_winax.msi",
            "version": "20.0.0.286",
            "sha1": "a1b73c662b7bce03ff2d8a729005e81036ea1a24"
        },
        {
            # Released 2/9/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer20_0r0_306_winax.msi",
            "version": "20.0.0.306",
            "sha1": "68ae4277d68146749cb6cf597d3d6be07422c372"
        },
        {
            # Released 3/10/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_182_winax.msi",
            "version": "21.0.0.182",
            "sha1": "717582fc7138c9cf4b3ec88413d38cddf8613d4c"
        },
        {
            # Released 3/23/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_197_winax.msi",
            "version": "21.0.0.197",
            "sha1": "1e81a4617abcbb95ee6bf9250be5a205ce0d289b"
        },
        {
            # Released 4/7/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_213_winax.msi",
            "version": "21.0.0.213",
            "sha1": "6d23ae1f12682b6baa1833c12955ca9adf7d13f2"
        },
        {
            # Released 5/12/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer21_0r0_242_winax.msi",
            "version": "21.0.0.242",
            "sha1": "01261660476cdcacf1872a8a5142018bce6de1dc"
        },
        {
            # Released 6/16/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer22_0r0_192_winax.msi",
            "version": "22.0.0.192",
            "sha1": "6aba77bca04f7170ac90c3852b837027f840b051"
        },
        {
            # Released 7/12/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer22_0r0_209_winax.msi",
            "version": "22.0.0.209",
            "sha1": "7db31a028cf14bdcdb4374fd941c08412130e384"
        },
        {
            # Released 9/13/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_162_winax.msi",
            "version": "23.0.0.162",
            "sha1": "4408e4b6c9ced6490d2b0b81d6a62d00776c8042"
        },
        {
            # Released 10/11/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_185_winax.msi",
            "version": "23.0.0.185",
            "sha1": "b86c4a79c445481992ac41c47a22323068ca40b1"
        },
        {
            # Released 10/26/2016
            "url": "https://cuckoo.sh/vmcloak/flashplayer23_0r0_205_winax.msi",
            "version": "23.0.0.205",
            "sha1": "c329a24860028263631411bd1c37369022473e9a"
        },
        {
            # Released 11/8/2016
            "url": "https://hatching.io/hatchvm/flashplayer23_0r0_207_winax.msi",
            "version": "23.0.0.207",
            "sha1": "699097fa5bbc4d3a0a9733108678ee642d1cc667"
        },
        {
            # Released 12/13/2016
            "url": "https://hatching.io/hatchvm/flashplayer24_0r0_186_winax.msi",
            "version": "24.0.0.186",
            "sha1": "f9828b0e872f71879664078dbaa23b05fff47494"
        },
        {
            # Released 1/10/2017
            "url": "https://hatching.io/hatchvm/flashplayer24_0r0_194_winax.msi",
            "version": "24.0.0.194",
            "sha1": "2d9648adf6fdc05cbc61b037ec5e434c7a73dfe4"
        },
        {
            # Released 2/14/2017
            "url": "https://hatching.io/hatchvm/flashplayer24_0r0_221_winax.msi",
            "version": "24.0.0.221",
            "sha1": "e8ac1c9c4e12ce7164b1f7374e6ef2868ab51e7f"
        },
        {
            # Released 03/14/2017
            "url": "https://hatching.io/hatchvm/flashplayer25_0r0_127_winax.msi",
            "version": "25.0.0.127",
            "sha1": "78618c96a0e65cc1ace1aedb0ecac04972b3ac7f"
        },
        {
            # Released 04/11/2017
            "url": "https://hatching.io/hatchvm/flashplayer25_0r0_148_winax.msi",
            "version": "25.0.0.148",
            "sha1": "e3907d0e0ac26a2db556ee6fa864243f3cb0a9f0"
        },
        {
            # Released 05/09/2017
            "url": "https://hatching.io/hatchvm/flashplayer25_0r0_171_winax.msi",
            "version": "25.0.0.171",
            "sha1": "780af04828e234a59ed297bcd31e4a08a0ce3364"
        },
        {
            # Released 06/13/2017
            "url": "https://hatching.io/hatchvm/flashplayer26_0r0_126_winax.msi",
            "version": "26.0.0.126",
            "sha1": "40dda6ea0f2a191a027fc6d4a61d2ee98636694e"
        },
        {
            # Released 06/16/2017
            "url": "https://hatching.io/hatchvm/flashplayer26_0r0_131_winax.msi",
            "version": "26.0.0.131",
            "sha1": "a1b5db1a5231740b64a8833b53f481b22402b430"
        },
        {
            # Released 07/11/2017
            "url": "https://hatching.io/hatchvm/flashplayer26_0r0_137_winax.msi",
            "version": "26.0.0.137",
            "sha1": "c7230247b1f1622016c38e4bedfdace9e49c6379"
        },
        {
            # Released 08/08/2017
            "url": "https://hatching.io/hatchvm/flashplayer26_0r0_151_winax.msi",
            "version": "26.0.0.151",
            "sha1": "6ebfb96f7c4c4c3d54a183cffaaa712c799982a5"
        },
        {
            # Released 09/12/2017
            "url": "https://hatching.io/hatchvm/flashplayer27_0r0_130_winax.msi",
            "version": "27.0.0.130",
            "sha1": "a37f295cc346912d959631f5301255790b495870"
        },
        {
            # Released 10/10/2017
            "url": "https://hatching.io/hatchvm/flashplayer27_0r0_159_winax.msi",
            "version": "27.0.0.159",
            "sha1": "fe243a4d9237b054346a750697eb25ed897492e7"
        },
        {
            # Released 10/16/2017
            "url": "https://hatching.io/hatchvm/flashplayer27_0r0_170_winax.msi",
            "version": "27.0.0.170",
            "sha1": "bf376fe52e6441a98c1a5b0686c11faf879af557"
        },
        {
            # Released 10/25/2017
            "url": "https://hatching.io/hatchvm/flashplayer27_0r0_183_winax.msi",
            "version": "27.0.0.183",
            "sha1": "f617731fce561af0451433daba4bc6b90c7673dd"
        },
        {
            # Released 11/14/2017
            "url": "https://hatching.io/hatchvm/flashplayer27_0r0_187_winax.msi",
            "version": "27.0.0.187",
            "sha1": "4c1e4dc52fbe26f53844cbbf18c5c3675c203895"
        },
        {
            # Released 12/12/2017
            "url": "https://hatching.io/hatchvm/flashplayer28_0r0_126_winax.msi",
            "version": "28.0.0.126",
            "sha1": "6ce0b7e7f813f32c51d34e454f19dc85529bc93f"
        },
        {
            # Released 01/09/2018
            "url": "https://hatching.io/hatchvm/flashplayer28_0r0_137_winax.msi",
            "version": "28.0.0.137",
            "sha1": "addd5ad5be2ae11868d2c8bcefd9396a30329fee"
        },
        {
            # Released 02/06/2018
            "url": "https://hatching.io/hatchvm/flashplayer28_0r0_161_winax.msi",
            "version": "28.0.0.161",
            "sha1": "240fec89d632534f1231475beee8eb4466b784b0"
        },
        {
            # Released 03/13/2018
            "url": "https://hatching.io/hatchvm/flashplayer29_0r0_113_winax.msi",
            "version": "29.0.0.113",
            "sha1": "cea86cb70ee72b7b968b94106b8ba2d231fd0a2b"
        },
        {
            # Released 04/10/2018
            "url": "https://hatching.io/hatchvm/flashplayer29_0r0_140_winax.msi",
            "version": "29.0.0.140",
            "sha1": "ed2d4358477b393438f455a7283d583fc98ef073"
        },
        {
            # Released 05/08/2018
            "url": "https://hatching.io/hatchvm/flashplayer29_0r0_171_winax.msi",
            "version": "29.0.0.171",
            "sha1": "f23fc2d65dd38efc3ce15f44e2c21118db65ede0"
        },
        {
            # Released 06/07/2018
            "url": "https://hatching.io/hatchvm/flashplayer30_0r0_113_winax.msi",
            "version": "30.0.0.113",
            "sha1": "9179639901137aeb153b737cb60554fe183757f1"
        },
        {
            # Released 07/10/2018
            "url": "https://hatching.io/hatchvm/flashplayer30_0r0_134_winax.msi",
            "version": "30.0.0.134",
            "sha1": "d8d922c8bc2b3604aa1b51455d99181a6e84b973"
        },
        {
            # Released 08/14/2018)
            "url": "https://hatching.io/hatchvm/flashplayer30_0r0_154_winax.msi",
            "version": "30.0.0.154",
            "sha1": "a3434a3d95d10bf9ab1ba08c8054749d25f93733"
        },
        {
            # Released 09/11/2018
            "url": "https://hatching.io/hatchvm/flashplayer31_0r0_108_winax.msi",
            "version": "31.0.0.108",
            "sha1": "c01a59040a1e707e1235c40defd7cafafe534bc6"
        },
        {
            # Released 10/09/2018
            "url": "https://hatching.io/hatchvm/flashplayer31_0r0_122_winax.msi",
            "version": "31.0.0.122",
            "sha1": "c831ab890facb906dc3608058cd3269919c39076"
        },
        {
            # Released 11/13/2018
            "url": "https://hatching.io/hatchvm/flashplayer31_0r0_148_winax.msi",
            "version": "31.0.0.148",
            "sha1": "a8cc46cc58195b03322dc0588ce692f2e4c97948"
        },
        {
            # Released 11/20/2018
            "url": "https://hatching.io/hatchvm/flashplayer31_0r0_153_winax.msi",
            "version": "31.0.0.153",
            "sha1": "23bf7580af5abb6e6717b94d8543a1f88bfb4992"
        },
        {
            # Released 12/05/2018
            "url": "https://hatching.io/hatchvm/flashplayer32_0r0_101_winax.msi",
            "version": "32.0.0.101",
            "sha1": "b5fb393a4ce018d0c1b094075f6dcbd72a72fa65"
        },
        {
            # Released 01/08/2019
            "url": "https://hatching.io/hatchvm/flashplayer32_0r0_114_winax.msi",
            "version": "32.0.0.114",
            "sha1": "5d74603b8156921b87720f8cdf6a9b95334b0cb6"
        },
        {
            # Released 02/12/2019
            "url": "https://hatching.io/hatchvm/flashplayer32_0r0_142_winax.msi",
            "version": "32.0.0.142",
            "sha1": "0682aae6e00ea3af2fd0702c1cb22d132d8f0e9b"
        },
        {
            # Released 03/12/2019
            "url": "https://hatching.io/hatchvm/flashplayer32_0r0_156_winax.msi",
            "version": "32.0.0.156",
            "sha1": "b7bb0248c95d5235faab09e73e9a7454a0a86c03"
        },
        {
            "version": "latest",
            "urls": [
                "https://fpdownload.macromedia.com/pub/flashplayer/latest/help/install_flash_player_ax.exe",
            ],
        }
    ]

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
