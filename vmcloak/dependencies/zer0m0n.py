# Copyright (C) 2017 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import pefile
import time

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

class Zer0m0n(Dependency):
    name = "zer0m0n"
    recommended = True

    # Disable ntoskrnl validation in winload.
    winload = {
        0x4ce7929c: 0x4bdc,
    }

    # Disable PatchGuard initialization.
    ntoskrnl_pg = {
        0x4ce7951a: 0x4d1568,
    }

    # Disable Driver Signature Enforcement (driver signing).
    ntoskrnl_ci = {
        0x4ce7951a: 0x36a8f0,
    }

    def patch_winload(self, blob):
        pe1 = pefile.PE(data=blob, fast_load=True)
        if pe1.FILE_HEADER.TimeDateStamp not in self.winload:
            log.warning(
                "Unsupported winload.exe: timestamp 0x%08x",
                pe1.FILE_HEADER.TimeDateStamp
            )
            return

        off = self.winload[pe1.FILE_HEADER.TimeDateStamp]
        buf = blob[:off] + "\xb0\x01\xc3\x90" + blob[off+4:]

        pe2 = pefile.PE(data=buf, fast_load=True)
        pe2.OPTIONAL_HEADER.CheckSum = pe2.generate_checksum()

        buf = pe2.write()

        count = 0
        for idx in xrange(len(blob)):
            if blob[idx] != buf[idx]:
                count += 1

        if count > 8:
            log.warning("Something went wrong rebuilding winload.exe!")
            return
        return buf

    def patch_ntoskrnl(self, blob):
        pe1 = pefile.PE(data=blob, fast_load=True)
        if pe1.FILE_HEADER.TimeDateStamp not in self.ntoskrnl_pg:
            log.warning(
                "Unsupported ntoskrnl.exe: timestamp=0x%08x",
                pe1.FILE_HEADER.TimeDateStamp
            )
            return

        # Disable PatchGuard initialization.
        off = self.ntoskrnl_pg[pe1.FILE_HEADER.TimeDateStamp]
        buf = blob[:off] + "\x90\x90" + blob[off+2:]

        # Always set g_CiEnabled to zero.
        off = self.ntoskrnl_ci[pe1.FILE_HEADER.TimeDateStamp]
        buf = buf[:off] + "\x00" + buf[off+1:]

        pe2 = pefile.PE(data=buf, fast_load=True)
        pe2.OPTIONAL_HEADER.CheckSum = pe2.generate_checksum()

        buf = pe2.write()

        count = 0
        for idx in xrange(len(blob)):
            if blob[idx] != buf[idx]:
                count += 1

        if count > 7:
            log.warning("Something went wrong rebuilding ntoskrnl.exe!")
            return
        return buf

    def new_bcd_entry(self):
        # Due to a bug with pythonw.exe & Cuckoo Agent <= 0.8 we can't run the
        # commands the way we want to (i.e., "stdin" should be set to
        # subprocess.PIPE in subprocess calls too). Dirty workaround follows.
        return """
import re
import subprocess
import sys

out = subprocess.check_output([
    "C:\\\\Windows\\\\Sysnative\\\\bcdedit.exe",
    "/copy", "{current}", "/d", "Secret",
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

guid = re.search("({[a-z0-9-]+})", out)
if not guid:
    sys.exit("Error creating BCD entry: out=%r err=%r" % (out, err))

guid = guid.group(1)

subprocess.check_output([
    "C:\\\\Windows\\\\Sysnative\\\\bcdedit.exe",
    "/timeout", "10",
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

subprocess.check_output([
    "C:\\\\Windows\\\\Sysnative\\\\bcdedit.exe",
    "/set", guid, "nointegritychecks", "1",
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

subprocess.check_output([
    "C:\\\\Windows\\\\Sysnative\\\\bcdedit.exe",
    "/set", guid, "path", "\\\\Windows\\\\System32\\\\osloader.exe",
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

subprocess.check_output([
    "C:\\\\Windows\\\\Sysnative\\\\bcdedit.exe",
    "/set", guid, "kernel", "ntkrnlmp.exe",
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

subprocess.check_output([
    "C:\\\\Windows\\\\Sysnative\\\\bcdedit.exe",
    "/default", guid,
], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        """.strip()

    def run(self):
        winload = self.a.retrieve("C:\\Windows\\Sysnative\\winload.exe")
        winload = self.patch_winload(winload)
        if not winload:
            return
        self.a.upload("C:\\Windows\\Sysnative\\osloader.exe", winload)

        ntoskrnl = self.a.retrieve("C:\\Windows\\Sysnative\\ntoskrnl.exe")
        ntoskrnl = self.patch_ntoskrnl(ntoskrnl)
        if not ntoskrnl:
            return
        self.a.upload("C:\\Windows\\Sysnative\\ntkrnlmp.exe", ntoskrnl)

        self.a.upload("C:\\pgdsepatch.py", self.new_bcd_entry())
        self.a.execpy("C:\\pgdsepatch.py", True)
        time.sleep(2)
        self.a.remove("C:\\pgdsepatch.py")
