from ctypes import c_char, c_ushort, c_uint, c_char_p
from ctypes import windll, Structure, POINTER, sizeof
import socket
from _winreg import CreateKeyEx, SetValueEx
from _winreg import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
from _winreg import KEY_SET_VALUE, REG_DWORD

from settings import HOST_IP, HOST_PORT, RESOLUTION


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

REGISTRY = [
    # Disable "Windows XP Tour" prompt.
    # http://www.techrepublic.com/article/tech-tip-disable-the-windows-xp-tour-prompt/
    (HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Applets\\Tour', 'RunCount', REG_DWORD, 0),

    # Disable the Windows Indexation service.
    # http://www.wikihow.com/Turn-Off-Windows-XP%E2%80%99s-Indexing-Service
    (HKEY_LOCAL_MACHINE, 'System\\CurrentControlSet\\Services\\CiSvc', 'Start', REG_DWORD, 4),
]


def set_resolution(width, height):
    dm = _DevMode()
    dm.dmSize = sizeof(dm)
    if not EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS, dm):
        return False

    dm.dmPelsWidth = width
    dm.dmPelsHeight = height

    ret = ChangeDisplaySettings(dm, CDS_UPDATEREGISTRY)
    return ret == DISP_CHANGE_SUCCESSFUL


def set_regkey(key, subkey, name, typ, value):
    parts = subkey.split('\\')
    for off in xrange(1, len(parts)):
        CreateKeyEx(key, '\\'.join(parts[:off]), 0, KEY_SET_VALUE).Close()

    with CreateKeyEx(key, subkey, 0, KEY_SET_VALUE) as handle:
        SetValueEx(handle, name, 0, typ, value)


if __name__ == '__main__':
    s = socket.create_connection((HOST_IP, HOST_PORT))

    width, height = [int(x) for x in RESOLUTION.split('x')]
    s.send('\x01' if set_resolution(width, height) else '\x00')

    for key, subkey, name, typ, value in REGISTRY:
        set_regkey(key, subkey, name, typ, value)
