from vmcloak.winxp import WindowsXP
from vmcloak.win7 import Windows7x86, Windows7x64
from vmcloak.win81 import Windows81x86, Windows81x64
from vmcloak.win10 import Windows10x86, Windows10x64

os_types = {
    "winxp": WindowsXP,
    "win7x86": Windows7x86,
    "win7x64": Windows7x64,
    "win81x86": Windows81x86,
    "win81x64": Windows81x64,
    "win10x86": Windows10x86,
    "win10x64": Windows10x64,
}

def network_interface(os_version):
    o = os_types[os_version]
    return o.nictype

def get_os(os_version):
    h = os_types[os_version]
    return h()
