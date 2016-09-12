# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import WindowsAutounattended

class Windows10(WindowsAutounattended):
    name = "win10"
    service_pack = 2
    interface = "Ethernet"

    # List of preferences when multiple Windows 10 types are available.
    preference = "pro", "enterprise", "home"

    dummy_serial_key = "W269N-WFGWX-YVC9B-4J6C9-T83GX"

class Windows10x64(Windows10):
    arch = "amd64"
    mount = "/mnt/win10x64", "/mnt/win10"

class Windows10x86(Windows10):
    arch = "x86"
    mount = "/mnt/win10x86", "/mnt/win10"
