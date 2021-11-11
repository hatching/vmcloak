# Copyright (C) 2014-2018 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path
import re
import shutil
import subprocess
import tempfile
import time
from ipaddress import ip_network

from vmcloak.constants import VMCLOAK_ROOT
from vmcloak.exceptions import DependencyError
from vmcloak.misc import (
    copytreelower, copytreeinto, sha1_file, ini_read, filename_from_url,
    download_file
)
from vmcloak.paths import get_path
from vmcloak.repository import deps_path
from vmcloak.verify import valid_serial_key
from vmcloak.rand import random_string

log = logging.getLogger(__name__)

GENISOIMAGE_WARNINGS = [
    b"Warning: creating filesystem that does not conform to ISO-9660.",
    b"Warning: creating filesystem that does not conform to ISO-9660. "
    b"Warning: creating filesystem with (nonstandard) Joliet extensions but "
    b"without (standard) Rock Ridge extensions. It is highly recommended to "
    b"add Rock Ridge",
]

class OperatingSystem(object):
    # Short name for this OS.
    name = None

    # Lowercase name of the OS: windows, ubuntu, etc.
    os_name = None

    # The version of the OS, 7, 10, 1804 (in case of ubuntu), etc. Must be a
    # lowercase string.
    os_version = None

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
        self.bootstrap_path = os.path.join(
            self.data_path, "bootstrap", self.os_name
        )
        self.serial_key = None

        if self.name is None:
            raise Exception("Name has to be provided for OS handler")

        if self.osdir is None:
            raise Exception("OSDir has to be provided for OS handler")

    def find_agent_binary(self):
        """Return the path of the agent binary for the OS name and
        architecture. Also return the file extension the binary should have
        when it is copied"""
        if not os.path.isdir(self.bootstrap_path):
            raise FileNotFoundError(
                f"Bootstrap path {self.bootstrap_path} for OS does not exist"
            )

        agent_arch_file = os.path.join(self.bootstrap_path, "agent", self.arch)
        with open(agent_arch_file, "r") as fp:
            agent_name = fp.read().strip()

        return os.path.join(self.bootstrap_path, "agent", agent_name), \
               os.path.splitext(agent_name)[1]

    def configure(self, tempdir, product):
        """Configure the setup with settings provided by the user."""
        self.tempdir = tempdir
        self.product = product

    def isofiles(self, outdir, tmp_dir=None, env_vars={}):
        """Abstract method for writing additional files to the newly created
        ISO file."""

    def set_serial_key(self, serial_key):
        """Abstract method for checking a serial key if provided and otherwise
        use a default serial key if available."""

    def pickmount(self, isomount=None):
        """Picks the first available mounted directory."""
        mounts = [isomount]

        if isinstance(self.mount, str):
            mounts.append(self.mount)
        else:
            mounts.extend(self.mount)

        for mount in mounts:
            if mount and os.path.isdir(mount) and os.listdir(mount):
                return mount

    def buildiso(self, mount, newiso, bootstrap, tmp_dir=None, env_vars={}):
        """Builds an ISO file containing all our modifications."""
        isocreate = get_path("genisoimage")
        if not isocreate:
            log.error("Either genisoimage or mkisofs is required!")
            return False

        outdir = tempfile.mkdtemp(dir=tmp_dir)
        # Copy all files to our temporary directory as mounted iso files are
        # read-only and we need lowercase (aka case-insensitive) filepaths.
        copytreelower(mount, outdir)

        # Copy the boot image.
        shutil.copy(os.path.join(self.path, "boot.img"), outdir)

        # Allow the OS handler to write additional files.
        self.isofiles(outdir, tmp_dir, env_vars=env_vars)

        bootstrap_copy = os.path.join(outdir, self.osdir, "vmcloak")
        os.makedirs(bootstrap_copy)
        for fname in os.listdir(self.bootstrap_path):
            filepath = os.path.join(self.bootstrap_path, fname)
            if not os.path.isfile(filepath):
                continue

            shutil.copy(filepath, os.path.join(bootstrap_copy, fname))

        # Find the correct agent binary for the current OS and architecture.
        try:
            agent_path, file_ext = self.find_agent_binary()
        except FileNotFoundError as e:
            log.error(
                f"Failed to find agent file for OS {self.os_name} with "
                f"architecture: {self.arch}. {e}"
            )
            shutil.rmtree(outdir)
            return False

        # Copy the agent binary to the tmp bootstrap folder with the extension
        # it should have, but using a normalized name.
        agent_name = f"{random_string(8, 16)}{file_ext}"
        shutil.copy(agent_path, os.path.join(bootstrap_copy, agent_name))
        env_vars["AGENT_FILE"] = agent_name
        env_vars["AGENT_RUNKEY"] = random_string(8, 16)

        # Write the configuration values for bootstrap.bat.
        with open(os.path.join(bootstrap_copy, "settings.bat"), "wb") as f:
            for key, value in env_vars.items():
                f.write(f"set {key}={value}\n".encode())

        copytreeinto(bootstrap, os.path.join(outdir, self.osdir))

        args = [
            isocreate, "-quiet", "-b", "boot.img", "-o", newiso,
        ] + self.genisoargs + [outdir]

        log.debug("Executing genisoimage: %s", " ".join(args))
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        warning = re.sub(b"[\\s]+", b" ", err).strip()
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

    os_name = "windows"
    nictype = "82540EM"
    osdir = os.path.join("sources", "$oem$", "$1")
    dummy_serial_key = None
    genisoargs = [
        "-no-emul-boot", "-iso-level", "2", "-udf", "-J", "-l", "-D", "-N",
        "-joliet-long", "-relaxed-filenames", "-allow-limited-size",
    ]

    def _autounattend_xml(self, product, ipaddress, gateway):
        values = {
            "PRODUCTKEY": self.serial_key,
            "COMPUTERNAME": random_string(8, 14),
            "USERNAME": random_string(8, 12),
            "PASSWORD": random_string(8, 16),
            "PRODUCT": product.upper(),
            "ARCH": self.arch,
            "INTERFACE": self.interface,
            "IPADDRESS": ipaddress,
            "DEFAULTGATEWAY": gateway
        }

        buf = open(os.path.join(self.path, "autounattend.xml"), "r").read()
        for key, value in values.items():
            buf = buf.replace(f"@{key}@", value)

        return buf

    def isofiles(self, outdir, tmp_dir=None, env_vars={}):
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

        ipnet = ip_network(
            f"{env_vars['GUEST_GATEWAY']}/{env_vars['GUEST_MASK']}",
            strict=False
        )

        unattend_xml = self._autounattend_xml(
            self.product or product,
            ipaddress=f"{env_vars['GUEST_IP']}/{ipnet.prefixlen}",
            gateway=env_vars["GUEST_GATEWAY"]
        )
        with open(os.path.join(outdir, "autounattend.xml"), "w") as f:
            f.write(unattend_xml)

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
    # Like depends, but specified per os name (win10x64, win7x64, etc)
    os_depends = {}
    must_reboot = False
    # Can multiple versions of this dependency be installed at the same time?
    multiversion = False
    exes = []
    tags = []
    files = []

    # OS versions in this list do not need an exe/installer etc.
    # If they are here and exes is not empty, do not stop the install.
    no_exe = []

    data_path = os.path.join(VMCLOAK_ROOT, "data")
    deps_path = deps_path

    def __init__(self, h=None, m=None, a=None, i=None, installer=None,
                 version=None, settings={}):
        self.h = h
        self.m = m
        self.a = a
        self.i = i
        self.installer = installer
        self.version = version or self.default
        self.arch = h.arch
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

            if "arch" in exe and exe["arch"] != self.arch:
                continue

            if "version" in exe and self.version and \
                    exe["version"] != self.version:
                continue

            self.exe = exe
            break
        else:
            if self.exes and self.i.osversion not in self.no_exe:
                log.error(
                    f"Could not find the correct installer"
                    f" {self.name} ({self.version or ''}) for "
                    f"'{i.osversion}' with "
                    f"architecture: '{self.arch}'"
                )
                raise DependencyError

        # Download the executable/installer or required files if there
        # are any.
        if self.exe or self.files:
            self.download()

        if self.check() is False:
            raise DependencyError("Check failed")

    @classmethod
    def get_dependencies(cls, image):
        if cls.depends:
            if isinstance(cls.depends, str):
                return [cls.depends]

            return cls.depends

        if cls.os_depends:
            deps = cls.os_depends.get(image.osversion, [])
            if isinstance(deps, str):
                return [deps]

            return deps

    def _do_downloads(self, filepaths_urllist_sha1_v):
        for filepath, urllist, expected_sha1, _, in filepaths_urllist_sha1_v:
            for url in urllist:
                success, sha1hash = download_file(url, filepath)
                if not success:
                    log.warning(f"Failed to download file from: {url}")
                    continue

                if expected_sha1 and sha1hash != expected_sha1:
                    log.warning(
                        f"Calculated sha1 hash '{sha1hash}' of downloaded "
                        f"file {filepath} did not match expected hash "
                        f"'{expected_sha1}'. File source: {url}"
                    )
                    os.remove(filepath)
                    continue

                # No issues with the download, do not download more.
                break

            if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
                raise DependencyError(
                    f"No valid file was downloaded from any of the sources: "
                    f"{', '.join(urllist)}"
                )

    def _find_downloadable_files(self, download_dictlist):
        downloadables = []
        for downloadable_file in download_dictlist:
            all_urls = []
            urls = downloadable_file.get("urls")
            if urls and isinstance(urls, list):
                all_urls.extend(urls)

            url = downloadable_file.get("url")
            if url and isinstance(url, str):
                all_urls.append(url)

            if not all_urls:
                raise KeyError(
                    f"No URLs to download file from. Invalid files or exes "
                    f"entry? {downloadable_file}"
                )

            filename = downloadable_file.get("filename") or \
                       filename_from_url(all_urls[0])

            if not filename:
                raise KeyError(
                    f"No filename in files/exes entry: {downloadable_file}"
                )

            downloadables.append(
                (os.path.join(deps_path, filename),
                 all_urls, downloadable_file.get("sha1"),
                 downloadable_file.get("version")),
            )

        return downloadables

    def download(self):
        downloadables = []
        try:
            if self.exe:
                exe_downloadable = self._find_downloadable_files([self.exe])
                # This will always only return 1 downloadable. Access its first
                # element, which is the filepath.
                self.filepath = exe_downloadable[0][0]
                self.filename = os.path.basename(self.filepath)
                downloadables.extend(exe_downloadable)

            if self.files:
                downloadables.extend(self._find_downloadable_files(self.files))
        except KeyError as e:
            raise DependencyError(f"Unable to get resource. {e}")

        # Check which of the downloadable files already exist.
        for downloadable in downloadables[:]:
            filepath, _, expected_sha1sum, version = downloadable
            # Skip check if we need the latest version. We cannot know what
            # the download file version is since we never know the hash of the
            # latest version.
            if version == "latest":
                continue

            if not os.path.exists(filepath):
                continue

            if expected_sha1sum and expected_sha1sum != sha1_file(filepath):
                continue

            # Remove downloadable file from download list because it exists
            # and it is the expected hash or there was no expected hash.
            downloadables.remove(downloadable)

        if downloadables:
            log.debug(
                f"Downloading (installation) files for dependency "
                f"'{self.name}'"
                f" {f'version={self.version}' if self.version else ''}"
            )
            self._do_downloads(downloadables)

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

    def upload_file(self, filepath, to_machine_filepath):
        """Upload the specified filepath to the specified machine filepath"""
        self.a.upload(to_machine_filepath, open(filepath, "rb"))

    def upload_dependency(self, filepath):
        """Upload this dependency to the specified filepath."""
        self.upload_file(self.filepath, filepath)

    def wait_process_appear(self, process_name):
        """Wait for a process to appear."""
        while True:
            time.sleep(1)

            for line in self.a.execute("tasklist")["stdout"].split("\n"):
                if line.lower().startswith(process_name.lower()):
                    return

    def wait_process_exit(self, process_name, timeout=None):
        """Wait for a process to exit."""
        waited = 0
        cmd = f"tasklist /FO TABLE /NH /FI \"IMAGENAME eq {process_name}\""
        while True:
            for line in self.a.execute(cmd)["stdout"].split("\n"):
                if line.lower().startswith(process_name.lower()):
                    log.debug("Waiting for %s to finish..", process_name)
                    break
            else:
                break

            if timeout and waited >= timeout:
                raise TimeoutError(
                    f"Process '{process_name}' did not exit after {waited} "
                    f"seconds."
                )

            time.sleep(1)
            waited += 1

    def run_powershell_command(self, command):
        return self.a.execute(
            f'powershell -ExecutionPolicy bypass "{command}"'
        )

    def run_powershell_strings(self, powershell_strings):
        script_winpath = f"c:\\{random_string(6, 10)}.ps1"
        self.a.upload(script_winpath, powershell_strings)
        try:
            return self.a.execute(
                f"powershell -ExecutionPolicy bypass -File {script_winpath}"
            )
        finally:
            self.a.remove(script_winpath)

    def run_powershell_file(self, powershell_file):
        script_winpath = f"c:\\{random_string(6, 10)}.ps1"
        self.upload_file(powershell_file, script_winpath)
        try:
            return self.a.execute(
                f"powershell -ExecutionPolicy bypass -File {script_winpath}"
            )
        finally:
            self.a.remove(script_winpath)
