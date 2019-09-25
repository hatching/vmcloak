# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path

VMCLOAK_ROOT = os.path.abspath(os.path.dirname(__file__))
VMCLOAK_VM_MODES = ["virtualbox", "kvm","iso"]

SNAPSHOT_XML_TEMPLATE = """<domainsnapshot>
  <name>{snapshot_name}</name>
</domainsnapshot>"""
