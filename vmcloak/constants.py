# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path

VMCLOAK_ROOT = os.path.abspath(os.path.dirname(__file__))
VMCLOAK_VM_MODES = ["virtualbox", "iso", "vmware"]

# https://www.makululinux.com/wp/newwiki/3d-support-for-vmware-guests-on-linux-hosts/
# https://kb.vmware.com/s/article/1003
_VMX_SVGA_TEMPLATE = """
mks.enable3d = "TRUE"
mks.gl.allowBlacklistedDrivers = "TRUE"
svga.autodetect = "FALSE"
svga.graphicsMemoryKB = "1048576"
svga.maxHeight = "%(reso_height)s"
svga.maxWidth = "%(reso_width)s"
svga.vramSize = "%(vram_size)s"
"""

# http://sanbarrow.com/vmx/vmx-scsi.html
# http://sanbarrow.com/vmx/vmx-ide.html
# If the filename points to a *.vmdk you can skip the device type
# %(adapter_type)s0.virtualDev = "%(virt_dev)s"
_VMX_HDD_TEMPLATE = """
%(adapter_type)s0.present = "TRUE"
%(adapter_type)s0:0.fileName = "%(vmdk_path)s"
%(adapter_type)s0:0.present = "TRUE"
%(adapter_type)s0.virtualDev = "%(virtual_dev)s"
"""

_VMX_CDROM = """
{adapter_type}0:0.deviceType = "{dev_type}"
{adapter_type}0:0.fileName = "{filename}"
{adapter_type}0:0.present = "TRUE"
{adapter_type}0:0.startConnected = "TRUE"
"""

_VMX_ETHERNET = """
ethernet{index}.connectionType = "{conn_type}"
ethernet{index}.virtualDev = "{vdev}"
ethernet{index}.present = "TRUE"
"""

_VMX_MAC = """
ethernet{index}.addressType = "{addr_type}"
ethernet{index}.address = "{mac_addr}"
ethernet{index}.checkMACAddress = "FALSE"
"""

_VMX_FLOPPY = """
floppy0.fileType = "{file_type}"
floppy0.fileName = "{file_name}"
floppy0.clientDevice = "FALSE"
floppy0.autodetect = "TRUE"
floppy0.present = "{present}"
"""

_VMX_VNC = """
RemoteDisplay.vnc.enabled = "TRUE"
RemoteDisplay.vnc.port = "{port}"
RemoteDisplay.vnc.password = "{password}"
RemoteDisplay.vnc.key = ""
RemoteDisplay.maxConnections = 1

"""

_VMX_vramsize_DEFAULT = 16777216
