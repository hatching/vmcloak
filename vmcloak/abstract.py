# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path
import random
import re
import shutil
import subprocess
import tempfile
import time

from vmcloak.conf import load_hwconf
from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.exceptions import DependencyError
from vmcloak.misc import copytreelower, copytreeinto, sha1_file, ini_read
from vmcloak.paths import get_path
from vmcloak.rand import random_serial, random_uuid, random_string
from vmcloak.repository import deps_path
from vmcloak.verify import valid_serial_key

log = logging.getLogger(__name__)

GENISOIMAGE_WARNINGS = [
    "Warning: creating filesystem that does not conform to ISO-9660.",
    "Warning: creating filesystem that does not conform to ISO-9660."
    " Warning: creating filesystem with (nonstandard) Joliet extensions but"
    " without (standard) Rock Ridge extensions. It is highly recommended to"
    " add Rock Ridge",
]


class Machinery(object):
    FIELDS = {}
    vm_dir_required = True
    data_dir_required = True

    def __init__(self, name):
        self.name = name
        self.network_idx = 0

    def vminfo(self, element=None):
        """Returns a dictionary with all available information for the
        Virtual Machine."""
        raise

    def create_vm(self):
        """Create a new Virtual Machine."""
        raise

    def delete_vm(self):
        """Delete an existing Virtual Machine and its associated files."""
        raise

    def ramsize(self, ramsize):
        """Modify the amount of RAM available for this Virtual Machine."""
        raise

    def vramsize(self, vramsize):
        """Modify the amount of Video memory available for this Virtual
        Machine."""
        raise

    def os_type(self, osversion):
        """Set the OS type."""
        raise

    def create_hd(self, fsize):
        """Create a harddisk."""
        raise

    def immutable_hd(self):
        """Make a harddisk immutable or normal."""
        raise

    def remove_hd(self):
        """Remove a harddisk."""
        raise

    def clone_hd(self, hdd_inpath, hdd_outpath):
        """Clone a harddisk."""
        raise

    def cpus(self, count):
        """Set the number of CPUs to assign to this Virtual Machine."""
        raise

    def attach_iso(self, iso):
        """Attach a ISO file as DVDRom drive."""
        raise

    def detach_iso(self):
        """Detach the ISO file in the DVDRom drive."""
        raise

    def set_field(self, key, value):
        """Set a specific field of a Virtual Machine."""
        raise

    def modify_mac(self, mac=None):
        """Modify the MAC address of a Virtual Machine."""
        raise

    def network_index(self):
        """Get the index for the next network interface."""
        ret = self.network_idx
        self.network_idx += 1
        return ret

    def hostonly(self, macaddr=None, index=1):
        """Configure a hostonly adapter for the Virtual Machine."""
        raise

    def nat(self, macaddr=None, index=1):
        """Configure NAT for the Virtual Machine."""
        raise

    def hwvirt(self, enable=True):
        """Enable or disable the usage of Hardware Virtualization."""
        raise

    def start_vm(self, visible=False):
        """Start the associated Virtual Machine."""
        raise

    def snapshot(self, label):
        """Take a snapshot of the associated Virtual Machine."""
        raise

    def stopvm(self):
        """Stop the associated Virtual Machine."""
        raise

    def list_settings(self):
        """List all settings of a Virtual Machine."""
        raise

    def init_vm(self, profile):
        """Initialize fields as specified by `FIELDS`."""
        hwconf = load_hwconf(profile=profile)

        def _init_vm(path, fields):
            for key, value in fields.items():
                key = path + "/" + key
                if isinstance(value, dict):
                    _init_vm(key, value)
                else:
                    if isinstance(value, tuple):
                        k, v = value
                        if k not in hwconf or not hwconf[k]:
                            value = "To be filled by O.E.M."
                        else:
                            if k not in config:
                                config[k] = random.choice(hwconf[k])

                            value = config[k][v]

                            # Some values have to be generated randomly.
                            if value is not None:
                                if value.startswith("<SERIAL>"):
                                    length = int(value.split()[-1])
                                    value = random_serial(length)
                                elif value.startswith("<UUID>"):
                                    value = random_uuid()

                    if value is None:
                        value = "To be filled by O.E.M."

                    log.debug("Setting %r to %r.", key, value)
                    ret = self.set_field(key, value)
                    if ret:
                        log.debug(ret)

        config = {}
        _init_vm("", self.FIELDS)


class OperatingSystem(object):
    # Short name for this OS.
    name = None

    # Service Pack that is likely being used.
    service_pack = None

    # Architecture this OS is aimed at (x86 or amd64).
    arch = None

    # Default directory where the original ISO is mounted.
    mount = None

    # The Network Interface Card Type.
    nictype = None

    # Directory where to store the vmcloak bootstrap files.
    osdir = None

    # Interface name in Windows
    interface = None

    # Additional arguments for genisoimage.
    genisoargs = []

    def __init__(self):
        self.data_path = os.path.join(VMCLOAK_ROOT, "data")
        self.path = os.path.join(self.data_path, self.name)
        self.serial_key = None

        if self.name is None:
            raise Exception("Name has to be provided for OS handler")

        if self.osdir is None:
            raise Exception("OSDir has to be provided for OS handler")

    def configure(self, tempdir, product):
        """Configure the setup with settings provided by the user."""
        self.tempdir = tempdir
        self.product = product

    def isofiles(self, outdir, tmp_dir=None):
        """Abstract method for writing additional files to the newly created
        ISO file."""

    def set_serial_key(self, serial_key):
        """Abstract method for checking a serial key if provided and otherwise
        use a default serial key if available."""

    def pickmount(self, isomount=None):
        """Picks the first available mounted directory."""
        mounts = [isomount]

        if isinstance(self.mount, basestring):
            mounts.append(self.mount)
        else:
            mounts.extend(self.mount)

        for mount in mounts:
            if mount and os.path.isdir(mount) and os.listdir(mount):
                return mount

    def buildiso(self, mount, newiso, bootstrap, tmp_dir=None):
        """Builds an ISO file containing all our modifications."""
        outdir = tempfile.mkdtemp(dir=tmp_dir)

        # Copy all files to our temporary directory as mounted iso files are
        # read-only and we need lowercase (aka case-insensitive) filepaths.
        copytreelower(mount, outdir)

        # Copy the boot image.
        shutil.copy(os.path.join(self.path, "boot.img"), outdir)

        # Allow the OS handler to write additional files.
        self.isofiles(outdir, tmp_dir)

        os.makedirs(os.path.join(outdir, self.osdir, "vmcloak"))

        data_bootstrap = os.path.join(self.data_path, "bootstrap")
        for fname in os.listdir(data_bootstrap):
            shutil.copy(os.path.join(data_bootstrap, fname),
                        os.path.join(outdir, self.osdir, "vmcloak", fname))

        copytreeinto(bootstrap, os.path.join(outdir, self.osdir))

        isocreate = get_path("genisoimage")
        if not isocreate:
            log.error("Either genisoimage or mkisofs is required!")
            shutil.rmtree(outdir)
            return False

        args = [
            isocreate, "-quiet", "-b", "boot.img", "-o", newiso,
        ] + self.genisoargs + [outdir]

        log.debug("Executing genisoimage: %s", " ".join(args))
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        warning = re.sub("[\\s]+", " ", err).strip()
        if p.wait() or out or warning not in GENISOIMAGE_WARNINGS:
            log.error(
                "Error creating ISO file (err=%d): %s %s",
                p.wait(), out, err
            )
            shutil.rmtree(outdir)
            return False

        shutil.rmtree(outdir)
        return True

class WindowsAutounattended(OperatingSystem):
    """Abstract wrapper around Windows-based Operating Systems that use the
    autounattend.xml file for automated installation, i.e., Windows 7+."""

    nictype = "82540EM"
    osdir = os.path.join("sources", "$oem$", "$1")
    dummy_serial_key = None
    genisoargs = [
        "-no-emul-boot", "-iso-level", "2", "-udf", "-J", "-l", "-D", "-N",
        "-joliet-long", "-relaxed-filenames",
    ]

    def _autounattend_xml(self, product):
        values = {
            "PRODUCTKEY": self.serial_key,
            "COMPUTERNAME": random_string(8, 14),
            "USERNAME": random_string(8, 12),
            "PASSWORD": random_string(8, 16),
            "PRODUCT": product.upper(),
            "ARCH": self.arch,
            "INTERFACE": self.interface,
        }

        buf = open(os.path.join(self.path, "autounattend.xml"), "rb").read()
        for key, value in values.items():
            buf = buf.replace("@%s@" % key, value)

        return buf

    def isofiles(self, outdir, tmp_dir=None):
        products = []

        product_ini = os.path.join(outdir, "sources", "product.ini")
        mode, conf = ini_read(product_ini)

        for line in conf.get("BuildInfo", []):
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key != "staged":
                continue

            for product in value.split(","):
                products.append(product.lower())

            break

        for preference in self.preference:
            if preference in products:
                product = preference
                break
        else:
            if products:
                product = products[0]
            else:
                product = self.preference[0]

        if self.product and self.product.lower() not in self.preference:
            log.error(
                "The product version of %s that was specified on the "
                "command-line is not known by us, ignoring it.", self.name
            )
            self.product = None

        with open(os.path.join(outdir, "autounattend.xml"), "wb") as f:
            f.write(self._autounattend_xml(self.product or product))

    def set_serial_key(self, serial_key):
        if serial_key and not valid_serial_key(serial_key):
            log.error("The provided serial key has an incorrect encoding.")
            log.info("Example encoding, AAAAA-BBBBB-CCCCC-DDDDD-EEEEE.")
            return False

        # https://technet.microsoft.com/en-us/library/jj612867.aspx
        self.serial_key = serial_key or self.dummy_serial_key
        return True

class Dependency(object):
    """Dependency instance. Each software has its own dependency class which
    informs VMCloak on how to install that particular piece of software."""
    name = None
    default = None
    recommended = False
    depends = None
    exes = []

    def __init__(self, h=None, m=None, a=None, i=None,
                 version=None, settings={}):
        self.h = h
        self.m = m
        self.a = a
        self.i = i
        self.version = version or self.default
        self.settings = settings
        self.exe = None
        self.filename = None

        self.init()

        # Emit settings directly into the instance. Should be fine.
        for target, value in settings.items():
            package, key = target.split(".", 1)
            if package == self.name:
                setattr(self, key, value)

        # Locate the matching installer.
        for exe in self.exes:
            if "target" in exe and exe["target"] != i.osversion:
                continue

            if "version" in exe and exe["version"] != self.version:
                continue

            if "arch" in exe and exe["arch"] != h.arch:
                continue

            self.exe = exe
            break
        else:
            if self.exes:
                log.error("Could not find the correct installer!")
                raise DependencyError

        # Download the dependency (if there is any to download).
        if self.exe:
            self.filename = os.path.basename(self.exe["url"])
            self.download()

        if self.check() is False:
            raise DependencyError

    def download(self):
        url, sha1 = self.exe["url"], self.exe["sha1"]
        self.filepath = os.path.join(deps_path, os.path.basename(url))
        if not os.path.exists(self.filepath) or \
                sha1_file(self.filepath) != sha1:
            subprocess.call(["wget", "-O", self.filepath, url])

        if sha1_file(self.filepath) != sha1:
            log.error("The checksum of %s doesn't match!", self.name)
            raise DependencyError

    def init(self):
        pass

    def check(self):
        pass

    def run(self):
        raise NotImplementedError

    def disable_autorun(self):
        """Disables AutoRun under Windows XP and Windows 7."""
        if self.h.name == "winxp":
            self.a.execute("reg add HKEY_LOCAL_MACHINE\\Software\\Microsoft\\"
                           "Windows\\CurrentVersion\\Policies\\Explorer "
                           "/v NoDriveTypeAutoRun /t REG_DWORD /d 177 /f")

        if self.h.name == "win7":
            self.a.execute("reg add HKEY_LOCAL_MACHINE\\Software\\Microsoft\\"
                           "Windows\\CurrentVersion\\Policies\\Explorer "
                           "/v NoDriveTypeAutoRun /t REG_DWORD /d 255 /f")

    def upload_dependency(self, filepath):
        """Upload this dependency to the specified filepath."""
        self.a.upload(filepath, open(self.filepath, "rb"))

    def wait_process_appear(self, process_name):
        """Wait for a process to appear."""
        while True:
            time.sleep(1)

            for line in self.a.execute("tasklist").json()["stdout"].split("\n"):
                if line.lower().startswith(process_name.lower()):
                    return

    def wait_process_exit(self, process_name):
        """Wait for a process to exit."""
        while True:
            time.sleep(1)

            for line in self.a.execute("tasklist").json()["stdout"].split("\n"):
                if line.lower().startswith(process_name.lower()):
                    log.info("Waiting for %s to finish..", process_name)
                    break
            else:
                break
