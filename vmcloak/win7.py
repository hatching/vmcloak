# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import WindowsAutounattended

class Windows7(WindowsAutounattended):
    name = "win7"
    service_pack = 2
    interface = "Local Area Connection"

    # List of preferences when multiple Windows 7 types are available.
    preference = "professional", "homepremium", "ultimate", "homebasic"

    dummy_serial_key = "33PXH-7Y6KF-2VJC9-XBBR8-HVTHH"

class Windows7x64(Windows7):
    arch = "amd64"
    mount = "/mnt/win7x64", "/mnt/win7"

class Windows7x86(Windows7):
    arch = "x86"
    mount = "/mnt/win7x86", "/mnt/win7"
