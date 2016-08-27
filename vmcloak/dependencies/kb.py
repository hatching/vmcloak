# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import time

from vmcloak.abstract import Dependency

class KB(Dependency):
    name = "kb"
    exes = [
        {
            "version": "2729094",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2729094-v2-x64.msu",
            "sha1": "e1a3ecc5030a51711f558f90dd1db52e24ce074b",
        },
        {
            "version": "2729094",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2729094-v2-x86.msu",
            "sha1": "565e7f2a6562ace748c5b6165aa342a11c96aa98",
        },
        {
            "version": "2731771",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2731771-x64.msu",
            "sha1": "98dba6673cedbc2860c76b9686e895664d463347",
        },
        {
            "version": "2731771",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2731771-x86.msu",
            "sha1": "86675d2fd327b328793dc179727ce0ce5107a72e",
        },
        {
            "version": "2533623",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2533623-x64.msu",
            "sha1": "8a59ea3c7378895791e6cdca38cc2ad9e83bebff",
        },
        {
            "version": "2533623",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2533623-x86.msu",
            "sha1": "25becc0815f3e47b0ba2ae84480e75438c119859",
        },
        {
            "version": "2670838",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2670838-x64.msu",
            "sha1": "9f667ff60e80b64cbed2774681302baeaf0fc6a6",
        },
        {
            "version": "2670838",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2670838-x86.msu",
            "sha1": "984b8d122a688d917f81c04155225b3ef31f012e",
        },
        {
            "version": "2786081",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2786081-x64.msu",
            "sha1": "dc63b04c58d952d533c40b185a8b555b50d47905",
        },
        {
            "version": "2786081",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2786081-x86.msu",
            "sha1": "70122aca48659bfb8a06bed08cb7047c0c45c5f4",
        },
        {
            "version": "2639308",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2639308-x64.msu",
            "sha1": "67eedaf061e02d503028d970515d88d8fe95579d",
        },
        {
            "version": "2639308",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2639308-x86.msu",
            "sha1": "96e09ef9caf3907a32315839086b9f576bb46459",
        },
        {
            "version": "2834140",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2834140-v2-x64.msu",
            "sha1": "3db9d9b3dc20515bf4b164821b721402e34ad9d6",
        },
        {
            "version": "2834140",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2834140-v2-x86.msu",
            "sha1": "b57c05e9da2c66e1bb27868c92db177a1d62b2fb",
        },
        {
            "version": "2882822",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2882822-x64.msu",
            "sha1": "ec92821f6ee62ac9d2f74e847f87be0bf9cfcb31",
        },
        {
            "version": "2882822",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2882822-x86.msu",
            "sha1": "7fab5b9ca9b5c2395b505d1234ee889941bfb151",
        },
        {
            "version": "2888049",
            "target": "win7x64",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2888049-x64.msu",
            "sha1": "fae6327b151ae04b56fac431e682145c14474c69",
        },
        {
            "version": "2888049",
            "target": "win7x86",
            "url": "https://cuckoo.sh/vmcloak/Windows6.1-KB2888049-x86.msu",
            "sha1": "65b4c7a5773fab177d20c8e49d773492e55e8d76",
        },
    ]

    def run(self):
        self.upload_dependency("C:\\setup.msu")
        self.a.execute("sc config wuauserv start= auto")
        time.sleep(1)
        self.a.execute("wusa.exe C:\\setup.msu /quiet /norestart")

        self.a.remove("C:\\setup.msu")

        self.a.execute("sc config wuauserv start= disabled")
        self.a.execute("net stop wuauserv")
