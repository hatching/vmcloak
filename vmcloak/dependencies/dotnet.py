# Copyright (C) 2015-2018 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class DotNet(Dependency):
    name = "dotnet"
    depends = "wic"
    default = "4.0"
    recommended = True
    exes = [{
        "version": "4.0",
        "urls": [
            "https://download.microsoft.com/download/9/5/A/95A9616B-7A37-4AF6-BC36-D6EA96C8DAAE/dotNetFx40_Full_x86_x64.exe",
            "https://cuckoo.sh/vmcloak/dotNetFx40_Full_x86_x64.exe",
        ],
        "sha1": "58da3d74db353aad03588cbb5cea8234166d8b99",
    }, {
        "version": "4.5",
        "urls": [
            "https://download.microsoft.com/download/b/a/4/ba4a7e71-2906-4b2d-a0e1-80cf16844f5f/dotnetfx45_full_x86_x64.exe",
            "https://cuckoo.sh/vmcloak/dotnetfx45_full_x86_x64.exe",
        ],
        "sha1": "b2ff712ca0947040ca0b8e9bd7436a3c3524bb5d",
    }, {
        "version": "4.5.1",
        "urls": [
            "https://download.microsoft.com/download/1/6/7/167F0D79-9317-48AE-AEDB-17120579F8E2/NDP451-KB2858728-x86-x64-AllOS-ENU.exe",
            "https://cuckoo.sh/vmcloak/NDP451-KB2858728-x86-x64-AllOS-ENU.exe",
        ],
        "sha1": "5934dd101414bbc0b7f1ee2780d2fc8b9bec5c4d",
    }, {
        "version": "4.5.2",
        "urls": [
            "https://download.microsoft.com/download/E/2/1/E21644B5-2DF2-47C2-91BD-63C560427900/NDP452-KB2901907-x86-x64-AllOS-ENU.exe",
            "https://cuckoo.sh/vmcloak/NDP452-KB2901907-x86-x64-AllOS-ENU.exe",
        ],
        "sha1": "89f86f9522dc7a8a965facce839abb790a285a63",
    }, {
        "version": "4.6",
        "urls": [
            "https://download.microsoft.com/download/C/3/A/C3A5200B-D33C-47E9-9D70-2F7C65DAAD94/NDP46-KB3045557-x86-x64-AllOS-ENU.exe",
            "https://cuckoo.sh/vmcloak/NDP46-KB3045557-x86-x64-AllOS-ENU.exe",
        ],
        "sha1": "3049a85843eaf65e89e2336d5fe6e85e416797be",
    }, {
        "version": "4.6.1",
        "urls": [
            "https://download.microsoft.com/download/E/4/1/E4173890-A24A-4936-9FC9-AF930FE3FA40/NDP461-KB3102436-x86-x64-AllOS-ENU.exe",
            "https://cuckoo.sh/vmcloak/NDP461-KB3102436-x86-x64-AllOS-ENU.exe",
        ],
        "sha1": "83d048d171ff44a3cad9b422137656f585295866",
    }, {
        "version": "4.6.2",
        "urls": [
            "https://download.microsoft.com/download/F/9/4/F942F07D-F26F-4F30-B4E3-EBD54FABA377/NDP462-KB3151800-x86-x64-AllOS-ENU.exe",
            "https://cuckoo.sh/vmcloak/NDP462-KB3151800-x86-x64-AllOS-ENU.exe",
        ],
        "sha1": "a70f856bda33d45ad0a8ad035f73092441715431",
    }, {
        "version": "4.7",
        "urls": [
            "https://download.microsoft.com/download/D/D/3/DD35CC25-6E9C-484B-A746-C5BE0C923290/NDP47-KB3186497-x86-x64-AllOS-ENU.exe",
            "https://cuckoo.sh/vmcloak/NDP47-KB3186497-x86-x64-AllOS-ENU.exe",
        ],
        "sha1": "76054141a492ba307595250bda05ad4e0694cdc3",
    }]

    def run(self):
        self.upload_dependency("C:\\setup.exe")
        self.a.execute("C:\\setup.exe /passive /norestart")
        self.a.remove("C:\\setup.exe")

class DotNet40(DotNet, Dependency):
    """Backwards compatibility."""
    name = "dotnet40"
    recommended = False
