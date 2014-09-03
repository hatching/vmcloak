from ctypes import c_char, c_ushort, c_uint, c_char_p, c_wchar_p
from ctypes import windll, Structure, POINTER, sizeof, byref, pointer
from ctypes.wintypes import HANDLE, DWORD, LPCWSTR, ULONG, LONG
import shutil
import socket
import subprocess
import tempfile
import random
import string
from _winreg import CreateKeyEx, SetValueEx
from _winreg import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, KEY_ALL_ACCESS
from _winreg import KEY_SET_VALUE, REG_DWORD, REG_SZ, REG_MULTI_SZ

from settings import HOST_IP, HOST_PORT, RESOLUTION
import logging


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

class UNICODE_STRING(Structure):
    _fields_ = [
        ('Length', c_ushort),
        ('MaximumLength', c_ushort),
        ('Buffer', c_wchar_p),
    ]

EnumDisplaySettings = windll.user32.EnumDisplaySettingsA
EnumDisplaySettings.argtypes = c_char_p, c_uint, POINTER(_DevMode)

ChangeDisplaySettings = windll.user32.ChangeDisplaySettingsA
ChangeDisplaySettings.argtypes = POINTER(_DevMode), c_uint

NtRenameKey = windll.ntdll.NtRenameKey
NtRenameKey.argtypes = HANDLE, POINTER(UNICODE_STRING)

RegOpenKeyExW = windll.advapi32.RegOpenKeyExW
RegOpenKeyExW.argtypes = HANDLE, LPCWSTR, DWORD, ULONG, POINTER(HANDLE)
RegOpenKeyExW.restype = LONG

RegCloseKey = windll.advapi32.RegCloseKey
RegCloseKey.argtypes = HANDLE,

ENUM_CURRENT_SETTINGS = -1
CDS_UPDATEREGISTRY = 1
DISP_CHANGE_SUCCESSFUL = 0

HARDDISK_NAMES = [
    'HD', 'HARDDISK', 'IBM', 'WD', 'Western Digital', 'Seagate',
    'HGST', 'Samsung', 'Harddisk', 'Drive', 'TB', 'GB', 'Desk',
    'IDE', 'SATA', 'USB', 'Desktop',
]

CD_NAMES = [
    'CD', 'CDROM', 'IBM', 'WD', 'Western Digital', 'Seagate', 'HGST',
    'Samsung', 'CD-ROM', 'Drive', 'TB', 'GB', 'Desk', 'IDE', 'SATA',
    'USB', 'BlueRay', 'Blue-Ray', 'DVD', 'DVD-ROM', 'DVD ROM', 'RW',
]

BIOS_NAMES = [
    'BIOS', '3.6', '5.4', 'System', 'Version', 'Award', 'AMI', 'EFI',
    'UEFI', 'Insyde', 'SeaBIOS',
]

VGA_BIOS_NAMES = [
    'BIOS', '3.6', '5.24', 'VGA', 'Version', 'Gigabyte', 'Dell',
    'Sapphire', 'Alienware', 'Gainward', 'Asus',
]


def random_string(length=6):
    """Create silly char combinations."""
    return ''.join(random.sample(string.letters, 6))


def generate_hd():
    """Generates a random harddisk name."""
    return ' '.join(random.sample(HARDDISK_NAMES, 3))


def generate_cd():
    """Generates a random CD name."""
    return ' '.join(random.sample(CD_NAMES, 3))


def generate_bios():
    """Generates a random BIOS name."""
    return ' '.join(random.sample(BIOS_NAMES, 3))


def generate_vga_bios():
    """Generates a random VGA BIOS name."""
    return ' '.join(random.sample(VGA_BIOS_NAMES, 3))


REGISTRY = [
    # Disable "Windows XP Tour" prompt.
    # http://www.techrepublic.com/article/tech-tip-disable-the-windows-xp-tour-prompt/
    (HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Applets\\Tour', 'RunCount', REG_DWORD, 0),

    # Disable the Windows Indexation service.
    # http://www.wikihow.com/Turn-Off-Windows-XP%E2%80%99s-Indexing-Service
    (HKEY_LOCAL_MACHINE, 'System\\CurrentControlSet\\Services\\CiSvc', 'Start', REG_DWORD, 4),

    # Cloak HD device identifier.
    (HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 0\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0', 'Identifier', REG_SZ, generate_hd()),

    # Cloak CDROM.
    (HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 1\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0', 'Identifier', REG_SZ, generate_cd()),

    # Cloak SystemBios Version.
    (HKEY_LOCAL_MACHINE, 'HARDWARE\\Description\\System', 'SystemBiosVersion', REG_MULTI_SZ, [generate_bios()]),

    # Cloak SystemBios Version.
    (HKEY_LOCAL_MACHINE, 'HARDWARE\\Description\\System', 'VideoBiosVersion', REG_MULTI_SZ, [generate_vga_bios(), generate_vga_bios()]),
]


class SetupWindows(object):
    def __init__(self, keep_evidence=False):
        self.log = logging.getLogger('Setup Windows')
        self.log.setLevel(logging.DEBUG)
        ch = logging.FileHandler('c:\\vmcloak\\windows_setup.log')
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                      '%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        self.keep_evidence = keep_evidence

    def set_resolution(self, width, height):
        """Set the screen resolution."""
        dm = _DevMode()
        dm.dmSize = sizeof(dm)
        if not EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS, dm):
            return False

        dm.dmPelsWidth = width
        dm.dmPelsHeight = height

        ret = ChangeDisplaySettings(dm, CDS_UPDATEREGISTRY)
        return ret == DISP_CHANGE_SUCCESSFUL

    def set_regkey(self, key, subkey, name, typ, value):
        """Set a specified registry key."""
        parts = subkey.split('\\')
        for off in xrange(1, len(parts)):
            CreateKeyEx(key, '\\'.join(parts[:off]), 0, KEY_SET_VALUE).Close()

        with CreateKeyEx(key, subkey, 0, KEY_SET_VALUE) as handle:
            SetValueEx(handle, name, 0, typ, value)
            self.log.info('Set value to %r %r', key, subkey)

    def rename_regkey(self, skey, ssubkey, dsubkey):
        res_handle = HANDLE()
        options = DWORD(0)
        res = RegOpenKeyExW(skey, ssubkey, options,
                            KEY_ALL_ACCESS, byref(res_handle))
        if not res:
            bsize = c_ushort(len(dsubkey) * 2)
            us = UNICODE_STRING()
            us.Buffer = c_wchar_p(dsubkey)
            us.Length = bsize
            us.MaximumLength = bsize

            res = NtRenameKey(res_handle, pointer(us))
            if res:
                self.log.error('Could not rename %r', ssubkey)
            else:
                self.log.info('Renamed %r to %r', ssubkey, dsubkey)

        if res_handle:
            RegCloseKey(res_handle)

    def run(self):
        """Modify the system settings."""
        self.log.info('Starting system modifications')

        # Read the agent.py file so we can drop it again later on.
        agent = open('C:\\vmcloak\\agent.py', 'rb').read()

        try:
            s = socket.create_connection((HOST_IP, HOST_PORT))

            width, height = [int(x) for x in RESOLUTION.split('x')]
            s.send('\x01' if self.set_resolution(width, height) else '\x00')
        except socket.error:
            self.log.error('Error connecting to socket')

        # Set registry keys.
        for key, subkey, name, typ, value in REGISTRY:
            self.set_regkey(key, subkey, name, typ, value)

        # Rename registry keys.
        self.rename_regkey(HKEY_LOCAL_MACHINE,
                           'HARDWARE\\ACPI\\DSDT\\VBOX__', random_string())

        self.rename_regkey(HKEY_LOCAL_MACHINE,
                           'HARDWARE\\ACPI\\FADT\\VBOX__', random_string())

        self.rename_regkey(HKEY_LOCAL_MACHINE,
                           'HARDWARE\\ACPI\\RSDT\\VBOX__', random_string())

        # Drop the agent and execute it.
        _, path = tempfile.mkstemp(suffix='.py')
        open(path, 'wb').write(agent)
        self.log.info('Agent dropped')

        # Don't wait for this process to end. Also, the agent will remove the
        # temporary agent file itself.
        subprocess.Popen(['C:\\Python27\\pythonw.exe', path])
        self.log.info('Started agent')

        # Remove all vmcloak files that are directly related. This does not
        # include the auxiliary directory or any of its contents.
        if not self.keep_evidence:
            shutil.rmtree('C:\\vmcloak')
        else:
            self.log.info('Keeping evidence')

        self.log.info('System modifications done')


if __name__ == '__main__':
    sw = SetupWindows(keep_evidence=False)
    sw.run()
