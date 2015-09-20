# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import argparse
import hashlib
import importlib
import json
import logging
import os
import pwd
import shutil
import socket
import stat
import subprocess
from ConfigParser import ConfigParser

from vmcloak.conf import Configuration
from vmcloak.constants import VMCLOAK_ROOT

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
    prefix = len(srcdir) + (not srcdir.endswith('/'))
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
        raise Exception('Cannot create directory if there is already '
                        'a file: %s' % dstdir)

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
        buf = open(path, 'rb').read()
    else:
        buf = ''

    # UTF-16 Byte Order Mark ("BOM")
    mode = 'utf16' if buf[:2] == '\xff\xfe' else 'latin1'
    buf = buf.decode(mode)

    for line in buf.split('\n'):
        line = line.strip()
        if not line or line[0] == ';':
            continue

        if line[0] == '[' and ']' in line:
            section = line[1:line.index(']')]
            ret[section] = []
            continue

        if '=' not in line:
            ret[section].append(line)
        else:
            a, b = line.split('=', 1)
            ret[section].append('%s=%s' % (a.strip(), b.strip()))
    return mode, ret

def ini_write(path, mode, data):
    lines = ['']
    for key in sorted(data.keys()):
        lines.append('[%s]' % key)
        for value in sorted(data[key]):
            lines.append(value)
        lines.append('')
    open(path, 'wb').write('\r\n'.join(lines).encode(mode))

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

            off = value.find('=')
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
    f = open(path, 'rb')

    while True:
        buf = f.read(1024*1024)
        if not buf:
            break

        h.update(buf)

    return h.hexdigest()

def read_birds():
    path = os.path.join(os.getenv('HOME'), '.vmcloak', 'birds.json')
    birds = {}

    if os.path.isfile(path):
        birds = json.load(open(path, 'rb'))

    return birds

def read_bird(name):
    return read_birds().get(name)

def add_bird(name, vmtype, hdd_path):
    path = os.path.join(os.getenv('HOME'), '.vmcloak', 'birds.json')

    birds = read_birds()
    birds[name] = dict(vmtype=vmtype, hdd_path=hdd_path)

    open(path, 'wb').write(json.dumps(birds))

def shared_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument('vmname', type=str, nargs='?', help='Name of the Virtual Machine.')
    parser.add_argument('--cuckoo', type=str, help='Directory where Cuckoo is located.')
    parser.add_argument('--vm-dir', type=str, help='Base directory for the virtual machine and its associated files.')
    parser.add_argument('--data-dir', type=str, help='Base directory for the virtual machine harddisks and images.')
    parser.add_argument('--vm', type=str, help='Virtual Machine Software (VirtualBox.)')
    parser.add_argument('--ramsize', help='Available virtual memory (in MB) for this virtual machine.')
    parser.add_argument('--resolution', type=str, help='Virtual Machine resolution.')
    parser.add_argument('--hdsize', help='Maximum size (in MB) of the dynamically allocated harddisk.')
    parser.add_argument('--host-ip', type=str, help='Static IP address to bind to on the Host.')
    parser.add_argument('--host-port', type=str, help='Port to bind to on the Host.')
    parser.add_argument('--hostonly-ip', type=str, help='Static IP address to use on the Guest for the hostonly network.')
    parser.add_argument('--hostonly-mask', type=str, help='Static IP address mask to use on the Guest for the hostonly network.')
    parser.add_argument('--hostonly-gateway', type=str, help='Static IP address gateway to use on the Guest for the hostonly network.')
    parser.add_argument('--hostonly-macaddr', type=str, help='Mac address for the hostonly interface.')
    parser.add_argument('--hostonly-adapter', type=str, help='Hostonly interface to use.')
    parser.add_argument('--nat', action='store_true', help='Name of the NAT network to attach to.')
    parser.add_argument('--dns-server', type=str, help='Address of DNS server to be used.')
    parser.add_argument('--hwvirt', action='store_true', default=None, help='Explicitly enable Hardware Virtualization.')
    parser.add_argument('--no-hwvirt', action='store_false', default=None, dest='hwvirt', help='Explicitly disable Hardware Virtualization.')
    parser.add_argument('--tags', type=str, help='Cuckoo Tags for the Virtual Machine.')
    parser.add_argument('--no-register-cuckoo', action='store_false', default=None, dest='register_cuckoo', help='Explicitly disable registering the Virtual Machine with Cuckoo upon completion.')
    parser.add_argument('--vboxmanage', type=str, help='Path to VBoxManage.')
    parser.add_argument('--vm-visible', action='store_true', default=None, help='Start the Virtual Machine in GUI mode.')
    parser.add_argument('--keyboard-layout', type=str, help='Keyboard Layout within the Virtual Machine.')
    parser.add_argument('--cpu-count', help='Number of CPUs to use with this Virtual Machine.')
    parser.add_argument('--vrde', action='store_true', help='Enable VRDE support in VirtualBox.')
    parser.add_argument('--vrde-port', type=int, help='Port for the VRDE server.')
    parser.add_argument('--vrde-password', type=str, help='Password for the VRDE server.')
    parser.add_argument('--hwconfig-profile', type=str, help='Take a particular hardware profile.')
    parser.add_argument('--auxiliary', type=str, help='Path to a directory containing auxiliary files that should be shipped to the Virtual Machine.')
    parser.add_argument('--auxiliary-local', type=str, help='Overwrite the directory path to the auxiliary files in the Virtual Machine.')
    parser.add_argument('--tempdir', type=str, help='Directory where to put temporary files.')
    parser.add_argument('--run-executable', type=str, help='Extra executable to be ran after full initialization of the Virtual Machine.')
    parser.add_argument('-s', '--settings', type=str, default=[], action='append', help='Configuration file with various settings.')
    parser.add_argument('-r', '--recommended-settings', action='store_true', help='Use the recommended settings.')
    parser.add_argument('-u', '--user', type=str, help='Drop user privileges to this user')
    parser.add_argument('-v', '--verbose', action='store_true', help='Display debug messages.')

    defaults = dict(
        vm='virtualbox',
        cuckoo='',
        ramsize=1024,
        resolution='1024x768',
        hdsize=256*1024,
        host_ip='192.168.56.1',
        host_port=0x4141,
        host_init_ip='192.168.56.2',
        host_init_mask='255.255.255.0',
        host_init_gateway='192.168.56.1',
        hostonly_ip='192.168.56.101',
        hostonly_mask='255.255.255.0',
        hostonly_gateway='192.168.56.1',
        hostonly_adapter=None,
        dns_server='8.8.8.8',
        tags='',
        vboxmanage='/usr/bin/VBoxManage',
        vm_visible=False,
        keyboard_layout='US',
        cpu_count=1,
        register_cuckoo=True,
        auxiliary_local='auxiliary',
        vrde=False,
        vrde_port=3389,
        vrde_password='vmcloak',
    )

    types = dict(
        ramsize=int,
        hdsize=int,
        cpu_count=int,
        host_port=int,
    )
    return parser, defaults, types

def register_cuckoo(hostonly_ip, tags, vmname, cuckoo_dirpath, rdp_port=None):
    log.debug('Registering the Virtual Machine with Cuckoo.')
    try:
        machine_py = os.path.join(cuckoo_dirpath, 'utils', 'machine.py')
        args = [
            machine_py, '--add',
            '--ip', hostonly_ip,
            '--platform', 'windows',
            '--tags', tags,
            '--snapshot', 'vmcloak',
            vmname,
        ]

        if rdp_port:
            args += ['--rdp_port', '%s' % rdp_port]

        subprocess.check_call(args, cwd=cuckoo_dirpath)
        return True
    except OSError as e:
        log.error('Is $CUCKOO/utils/machine.py executable? -> %s', e)
        return False
    except subprocess.CalledProcessError as e:
        log.error('Error registering the VM: %s.', e)
        return False

def wait_for_host(ipaddr, port):
    # Wait for the Agent to come up with a timeout of 1 second.
    while True:
        try:
            socket.create_connection((ipaddr, port), 1).close()
            break
        except socket.error:
            pass

def resolve_parameters(args, defaults, types, drop_user=False):
    s = Configuration()

    if args.recommended_settings:
        s.from_file(os.path.join(VMCLOAK_ROOT, 'data', 'recommended.ini'))

    for settings in args.settings:
        s.from_file(settings)

    s.from_args(args)
    s.from_defaults(defaults)
    s.apply_types(types)

    if s.user and not drop_user:
        try:
            user = pwd.getpwnam(s.user)
            os.setgroups((user.pw_gid,))
            os.setgid(user.pw_gid)
            os.setuid(user.pw_uid)
            os.environ['HOME'] = user.pw_dir
        except KeyError:
            raise Exception('Invalid user specified to drop '
                            'privileges to: %s' % s.user)
        except OSError as e:
            raise Exception('Failed to drop privileges: %s' % e)

        # Resolve the parameters again, but this time without applying the
        # user argument. This way paths that use os.getenv('HOME') will be
        # correct.
        return resolve_parameters(args, defaults, types, drop_user=True)

    return s

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
