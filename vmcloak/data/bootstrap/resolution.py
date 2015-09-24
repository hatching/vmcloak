# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import sys

from ctypes import c_char, c_ushort, c_uint, c_char_p
from ctypes import windll, Structure, POINTER, sizeof

# http://blogs.technet.com/b/heyscriptingguy/archive/2010/07/07/hey-scripting-guy-how-can-i-change-my-desktop-monitor-resolution-via-windows-powershell.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd183565(v=vs.85).aspx
class _DevMode(Structure):
    _fields_ = [
        ('dmDeviceName', c_char * 32),
        ('unused1', c_ushort * 2),
        ('dmSize', c_ushort),
        ('unused2', c_ushort),
        ('unused3', c_uint * 8),
        ('dmFormName', c_char * 32),
        ('dmLogPixels', c_ushort),
        ('dmBitsPerPel', c_ushort),
        ('dmPelsWidth', c_uint),
        ('dmPelsHeight', c_uint),
        ('unused2', c_uint * 10),
    ]

EnumDisplaySettings = windll.user32.EnumDisplaySettingsA
EnumDisplaySettings.argtypes = c_char_p, c_uint, POINTER(_DevMode)

ChangeDisplaySettings = windll.user32.ChangeDisplaySettingsA
ChangeDisplaySettings.argtypes = POINTER(_DevMode), c_uint

ENUM_CURRENT_SETTINGS = -1
CDS_UPDATEREGISTRY = 1
DISP_CHANGE_SUCCESSFUL = 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s <width> <height>" % sys.argv[0]
        exit(1)

    dm = _DevMode()
    dm.dmSize = sizeof(dm)
    if not EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS, dm):
        print "Error enumerating display settings.."
        exit(1)

    dm.dmPelsWidth = int(sys.argv[1])
    dm.dmPelsHeight = int(sys.argv[2])

    ret = ChangeDisplaySettings(dm, CDS_UPDATEREGISTRY)
    if ret != DISP_CHANGE_SUCCESSFUL:
        print "Error changing display settings.."
        exit(1)
