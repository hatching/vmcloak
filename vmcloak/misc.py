# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import hashlib
import importlib
import logging
import os
import shutil
import socket
import stat
import struct
import subprocess
import sys

from ConfigParser import ConfigParser

try:
    import pwd
    HAVE_PWD = True
except ImportError:
    HAVE_PWD = False

log = logging.getLogger(__name__)

def copytreelower(srcdir, dstdir):
    """Copies the source directory as lowercase to the destination directory.

    Lowercase as in, all directory and filenames are translated to lowercase,
    thus emulating Windows case-insensitive filepaths.

    """
    # If the source directory doesn't end with a slash then we have to take
    # this into account when slicing it later on. Namely, when the source
    # directory is "/mnt/winxp" then we slice up to "/mnt/winxp/", thus we
    # require one extra character for the slash. When the source directory is
    # "/mnt/winxp/" then of course we don't an extra character for the slice.
    prefix = len(srcdir) + (not srcdir.endswith("/"))
    for dirpath, dirnames, filenames in os.walk(srcdir):
        for dirname in dirnames:
            os.mkdir(os.path.join(dstdir,
                                  dirpath[prefix:].lower(),
                                  dirname.lower()))

        for fname in filenames:
            path = os.path.join(dirpath, fname)[prefix:]

            # Copy the file.
            shutil.copyfile(os.path.join(srcdir, path),
                            os.path.join(dstdir, path.lower()))

            # Make the file writable.
            os.chmod(os.path.join(dstdir, path.lower()),
                     stat.S_IRUSR | stat.S_IWUSR)

def copytreeinto(srcdir, dstdir):
    """Copy one directory into another directory.

    Unlike shutil.copytree() this function doesn't require the destination
    directory to be non-existing.

    """
    if os.path.isfile(dstdir):
        raise Exception("Cannot create directory if there is already "
                        "a file: %s" % dstdir)

    if not os.path.isdir(dstdir):
        os.mkdir(dstdir)

    for fname in os.listdir(srcdir):
        path_in = os.path.join(srcdir, fname)
        path_out = os.path.join(dstdir, fname)

        if os.path.isfile(path_in):
            shutil.copy(path_in, path_out)
        else:
            copytreeinto(path_in, path_out)

def ini_read(path):
    ret, section = {}, None

    if os.path.exists(path):
        buf = open(path, "rb").read()
    else:
        buf = ""

    # UTF-16 Byte Order Mark ("BOM")
    mode = "utf16" if buf[:2] == "\xff\xfe" else "latin1"
    buf = buf.decode(mode)

    for line in buf.split("\n"):
        line = line.strip()
        if not line or line[0] == ";":
            continue

        if line[0] == "[" and "]" in line:
            section = line[1:line.index("]")]
            ret[section] = []
            continue

        if "=" not in line:
            ret[section].append(line)
        else:
            a, b = line.split("=", 1)
            ret[section].append("%s=%s" % (a.strip(), b.strip()))
    return mode, ret

def ini_write(path, mode, data):
    lines = [""]
    for key in sorted(data.keys()):
        lines.append("[%s]" % key)
        for value in sorted(data[key]):
            lines.append(value)
        lines.append("")
    open(path, "wb").write("\r\n".join(lines).encode(mode))

def ini_add(data, section, value):
    if section not in data:
        data[section] = []

    if value not in data[section]:
        data[section].append(value)

def ini_delete(data, section, value):
    if section not in data:
        return

    for idx, row in enumerate(data[section]):
        if row == value:
            del data[section][idx]

def ini_merge(data, ini2, overwrite=True):
    mode, data2 = ini_read(ini2)
    for section in data2:
        for value in data2[section]:
            if section not in data:
                data[section] = [value]
                continue

            off = value.find("=")
            # If this line is not a key = value entry, then
            # we take the entire line.
            if off < 0:
                off = len(value)

            for idx, row in enumerate(data[section]):
                if len(row) > off and row[:off] == value[:off]:
                    if overwrite:
                        data[section][idx] = value
                    break
            else:
                data[section].append(value)

def ini_read_dict(path):
    c = ConfigParser()
    c.read(path)

    ret = {}
    for section in c.sections():
        ret[section] = dict(c.items(section))
    return ret

def sha1_file(path):
    """Calculate the sha1 hash of a file."""
    h = hashlib.sha1()
    f = open(path, "rb")

    while True:
        buf = f.read(1024*1024)
        if not buf:
            break

        h.update(buf)

    return h.hexdigest()

def register_cuckoo(hostonly_ip, tags, vmname, cuckoo_dirpath, rdp_port=None):
    log.debug("Registering the Virtual Machine with Cuckoo.")

    # Legacy Cuckoo setup.
    machine_py = os.path.join(cuckoo_dirpath, "utils", "machine.py")
    if os.path.exists(machine_py):
        try:
            args = [
                machine_py, "--add",
                "--ip", hostonly_ip,
                "--platform", "windows",
                "--tags", tags or "",
                "--snapshot", "vmcloak",
                vmname,
            ]

            if rdp_port:
                args += ["--rdp_port", "%s" % rdp_port]

            subprocess.check_call(args, cwd=cuckoo_dirpath)
            return True
        except OSError as e:
            log.error("Is $CUCKOO/utils/machine.py executable? -> %s", e)
            return False
        except subprocess.CalledProcessError as e:
            log.error("Error registering the VM: %s.", e)
            return False
        return

    # Cuckoo Package setup.
    try:
        args = [
            "cuckoo",
            "--cwd", cuckoo_dirpath,
            "machine",
            "--add", vmname, hostonly_ip,
            "--platform", "windows",
            "--tags", tags or "",
            "--snapshot", "vmcloak",
            "--options", "",
        ]
        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        log.error("Error registering VM: %s", e)
        return False

def wait_for_host(ipaddr, port):
    # Wait for the Agent to come up with a timeout of 1 second.
    while True:
        try:
            log.debug("Waiting for host %s", ipaddr)
            socket.create_connection((ipaddr, port), 1).close()
            break
        except socket.error:
            pass

def drop_privileges(user):
    if not HAVE_PWD:
        sys.exit(
            "This Operating System does not support the pwd module, please "
            "don't use privilege dropping."
        )

    try:
        user = pwd.getpwnam(user)
        os.setgroups((user.pw_gid,))
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)
        os.environ["HOME"] = user.pw_dir
    except KeyError:
        sys.exit("Invalid user specified to drop privileges to: %s" % user)
    except OSError as e:
        sys.exit("Failed to drop privileges: %s" % e)

def import_plugins(dirpath, module_prefix, namespace, class_):
    """Import plugins of type `class` located at `dirpath` into the
    `namespace` that starts with `module_prefix`. If `dirpath` represents a
    filepath then it is converted into its containing directory."""
    if os.path.isfile(dirpath):
        dirpath = os.path.dirname(dirpath)

    for fname in os.listdir(dirpath):
        if fname.endswith(".py") and not fname.startswith("__init__"):
            module_name, _ = os.path.splitext(fname)
            importlib.import_module("%s.%s" % (module_prefix, module_name))

    plugins = []
    for subclass in class_.__subclasses__():
        namespace[subclass.__name__] = subclass
        plugins.append(subclass)
    return plugins

def ipaddr_increase(ipaddr):
    """Increases the IP address."""
    addr = struct.unpack(">I", socket.inet_aton(ipaddr))[0]
    return socket.inet_ntoa(struct.pack(">I", addr + 1))
