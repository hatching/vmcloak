# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.


VBOX_CONFIG = {
    'VBoxInternal/Devices/pcbios/0/Config': dict(

        # http://blog.prowling.nu/2012/08/modifying-virtualbox-settings-for.html
        DmiBIOSVendor=('bios', 'vendor'),
        DmiBIOSVersion=('bios', 'version'),
        DmiBIOSReleaseDate=('bios', 'release_date'),
        # DmiBIOSReleaseMajor=
        # DmiBIOSReleaseMinor=
        # DmiBIOSFirmwareMajor=
        # DmiBIOSFirmwareMinor=

        DmiSystemVendor=('system', 'vendor'),
        DmiSystemProduct=('system', 'product'),
        DmiSystemVersion=('system', 'version'),
        DmiSystemSerial=('system', 'serial'),
        DmiSystemSKU=('system', 'sku'),
        DmiSystemFamily=('system', 'family'),
        DmiSystemUuid=('system', 'uuid'),

        # http://blog.prowling.nu/2012/10/modifying-virtualbox-settings-for.html
        DmiBoardVendor=('board', 'vendor'),
        DmiBoardProduct=('board', 'product'),
        DmiBoardVersion=('board', 'version'),
        DmiBoardSerial=('board', 'serial'),
        DmiBoardAssetTag=('board', 'asset'),
        DmiBoardLocInChass=('board', 'location'),

        DmiChassisVendor=('chassis', 'vendor'),
        DmiChassisVersion=('chassis', 'version'),
        DmiChassisSerial=('chassis', 'serial'),
        DmiChassisAssetTag=('chassis', 'asset'),
    ),
    'VBoxInternal/Devices/piix3ide/0/Config': {
        'Port0': dict(

            # http://downloads.cuckoosandbox.org/slides/blackhat.pdf, Page 82
            # https://forums.virtualbox.org/viewtopic.php?f=1&t=48718
            # ATAPIProductId='',
            # ATAPIRevision='',
            # ATAPIVendorId='',
        ),
        'PrimaryMaster': dict(

            # http://blog.prowling.nu/2012/08/modifying-virtualbox-settings-for.html
            SerialNumber=('harddisk', 'serial'),
            FirmwareRevision=('harddisk', 'revision'),
            ModelNumber=('harddisk', 'model'),
        ),
    },
}
