# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import WindowsAutounattended

class Windows81(WindowsAutounattended):
    name = "win81"
    service_pack = 2
    interface = "Ethernet"

    # List of preferences when multiple Windows 8.1 types are available.
    preference = "pro", "enterprise", "home"

    dummy_serial_key = "GCRJD-8NW9H-F2CDX-CCM8D-9D6T9"

class Windows81x64(Windows81):
    arch = "amd64"
    mount = "/mnt/win81x64", "/mnt/win81"

class Windows81x86(Windows81):
    arch = "x86"
    mount = "/mnt/win81x86", "/mnt/win81"
