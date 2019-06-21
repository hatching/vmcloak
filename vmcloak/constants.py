# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path

VMCLOAK_ROOT = os.path.abspath(os.path.dirname(__file__))
VMCLOAK_VM_MODES = ["virtualbox", "iso", "vmware"]

# https://www.makululinux.com/wp/newwiki/3d-support-for-vmware-guests-on-linux-hosts/
# https://kb.vmware.com/s/article/1003
_VMX_SVGA_TEMPLATE = """
mks.enable3d = “TRUE”
mks.gl.allowBlacklistedDrivers = “TRUE”
svga.autodetect = "FALSE"
svga.graphicsMemoryKB = "1048576"
svga.maxHeight = "%(reso_height)s"
svga.maxWidth = "%(reso_width)s"
svga.vramSize = "%(vram_size)s"
"""

_VMX_vramsize_DEFAULT = 16777216
