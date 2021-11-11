# Copyright (C) 2014-2017 Jurriaan Bremer.
# Copyright (C) 2018-2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
from ipaddress import ip_address, ip_network
from json import load
from os.path import join, exists
from sys import modules

from sqlalchemy import Integer, Text, String, inspect
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship, reconstructor

SCHEMA_VERSION = "d6c5bf858df1"

conf_path = os.path.join(os.getenv("HOME"), ".vmcloak")
image_path = os.path.join(conf_path, "image")
vms_path = os.path.join(conf_path, "vms")
deps_path = os.path.join(conf_path, "deps")
iso_dst_path = os.path.join(conf_path, "iso")

repository = join(conf_path, "repository.db")
engine = create_engine("sqlite:///%s" % repository)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class AlembicVersion(Base):
    """Database schema version. Used for automatic database migrations."""
    __tablename__ = "alembic_version"

    version_num = Column(String(32), nullable=False, primary_key=True)

def db_migratable():
    ses = Session()
    try:
        v = ses.query(AlembicVersion.version_num).first()
        return v is None or v.version_num != SCHEMA_VERSION
    finally:
        ses.close()

class Image(Base):
    """Represents each image that is created and altered along the way."""

    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    mode = Column(String(16))
    vm = Column(String(16))
    name = Column(String(64))
    path = Column(Text)
    osversion = Column(String(32))
    servicepack = Column(String(32))
    ipaddr = Column(String(32))
    port = Column(Integer)
    adapter = Column(String(32))
    netmask = Column(String(32))
    gateway = Column(String(32))
    cpus = Column(Integer)
    ramsize = Column(Integer)
    vramsize = Column(Integer)
    paravirtprovider = Column(String(32), default="default")
    mac = Column(String(32))
    _installed = Column(Text)

    @reconstructor
    def _init(self):
        self._net_obj = None

    @hybrid_property
    def installed(self):
        if not self._installed:
            return set()

        installed = set()
        for dep_version in self._installed.split(","):
            dep, version = dep_version.split(":")
            if not version:
                version = None

            installed.add((dep, version))

        return installed

    @installed.setter
    def installed(self, installed_list):
        if not isinstance(installed_list, (list, set)):
            raise TypeError(
                "Installed_list must be a list or set of (dep, version) "
                "entries"
            )

        if isinstance(installed_list, list):
            installed_list = set(installed_list)

        self._installed = ",".join(
            set(f"{dep}:{version}" if version else f"{dep}:"
                for dep, version in installed_list)
        )

    def add_installed_versions(self, deps_versions):
        if not isinstance(deps_versions, (list, set)):
            deps_versions = set([deps_versions])

        if isinstance(deps_versions, list):
            deps_versions = set(deps_versions)

        installed = self.installed
        installed.update(deps_versions)
        self.installed = installed

    def dependency_installed(self, depname, version=None):
        if version:
            return (depname, version) in self.installed

        for name, _ in self.installed:
            if name == depname:
                return True

        return False

    @property
    def platform(self):
        return platform(self.vm)

    @property
    def network(self):
        if not self._net_obj:
            self._net_obj = IPNet(
                network_notation=f"{self.ipaddr}/{self.netmask}",
                bridge_ip=self.gateway, bridge_interface=self.adapter
            )

        return self._net_obj

    def VM(self):
        return platform(self.vm).VM(self.name)

    def attr(self):
        translate = {"ipaddr": "ip"}
        attr = {}
        for k in ("path", "osversion", "servicepack", "ipaddr", "port",
                  "adapter", "netmask", "gateway", "cpus", "ramsize",
                  "vramsize", "paravirtprovider", "mac"):
            field = translate.get(k, k)
            attr[field] = getattr(self, k)
        return attr

class Snapshot(Base):
    """Represents each snapshot that has been created."""
    __tablename__ = "snapshot"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("image.id"))
    image = relationship("Image", backref="snapshots")
    # TODO: only (image.vm, vmname) have to be unique, although this doesn't
    # work with the current directory layout
    vmname = Column(String(64), nullable=False, unique=True)
    ipaddr = Column(String(32))
    port = Column(Integer)
    hostname = Column(String(32))
    mac = Column(String(32))

    @property
    def platform(self):
        return platform(self.image.vm)

    def VM(self):
        return platform(self.image.vm).VM(self.vmname)

if not os.path.isdir(conf_path):
    os.mkdir(conf_path)

db_exists = os.path.exists(repository)
if not db_exists:
    Base.metadata.create_all(engine)
    ses = Session()
    try:
        v = AlembicVersion()
        v.version_num = SCHEMA_VERSION
        ses.add(v)
        ses.commit()
    finally:
        ses.close()

elif db_exists:
    if not inspect(engine).has_table(AlembicVersion.__tablename__):
        AlembicVersion.__table__.create(engine)


if not os.path.isdir(image_path):
    os.mkdir(image_path)

if not os.path.isdir(deps_path):
    os.mkdir(deps_path)

if not os.path.isdir(iso_dst_path):
    os.mkdir(iso_dst_path)

def platform(name):
    full = 'vmcloak.platforms.' + name
    m = modules.get(full)
    if not m:
        m = __import__(full)
        m = getattr(m.platforms, name)
        if hasattr(m, 'initialize'):
            m.initialize()
    return m

# TODO: helper function to create missing/fix broken sidecar

# TODO
# {{{
def import_image(name):
    full_path = join(image_path, name)
    if name.endswith('.json'):
        return
    elif name.endswith('.vdi'):
        sidecar = full_path[:-4] + '.json'
        if exists(sidecar):
            attr = load(open(sidecar, 'rb'))
        else:
            attr = {}
        return Image(full_path, name[:-4], attr, platform('virtualbox'))
    else:
        raise NotImplementedError(name)

def import_snapshot(name):
    full_path = join(vms_path, name)
    if exists(join(full_path, name + '.vbox')):
        sidecar = join(full_path, name + '.json')
        if exists(sidecar):
            attr = load(open(sidecar, 'rb'))
        else:
            attr = {}
        return Snapshot(full_path, name, attr, platform('virtualbox'))
    else:
        raise NotImplementedError(name)
# }}}

def list_images():
    s = Session()
    return s.query(Image).all()

def find_used_ips():
    s = Session()
    ips = set()
    try:
        for image in s.query(Image).all():
            ips.add((image.gateway, f"{image.name} gateway"))
            ips.add((image.ipaddr, f"{image.name} IP"))
            for snap in image.snapshots:
                ips.add(
                    (snap.ipaddr, f"Image {image.name} snapshot {snap.vmname}")
                )
    finally:
        s.close()

    return ips

def list_snapshots():
    s = Session()
    return s.query(Snapshot).all()

def any_from_name(name):
    s = Session()
    snap = s.query(Snapshot).filter_by(vmname=name).first()
    if snap:
        return snap
    img = s.query(Image).filter_by(name=name).first()
    return img

def find_snapshot(name):
    s = Session()
    return s.query(Snapshot).filter_by(vmname=name).first()

def remove_image(name):
    s = Session()
    img = s.query(Image).filter_by(name=name).first()
    if img:
        s.delete(img)
        s.commit()

def remove_snapshot(name):
    s = Session()
    snap = s.query(Snapshot).filter_by(vmname=name).first()
    if snap:
        s.delete(snap)
        s.commit()

def find_vm(name):
    s = Session()
    img = s.query(Image).filter_by(name=name).first()
    if img:
        return False, img
    snap = s.query(Snapshot).filter_by(vmname=name).first()
    if snap:
        return True, snap
    return False, None

def find_image(name):
    session = Session()
    return session.query(Image).filter_by(name=name).first()

def image_has_snapshots(name):
    s = Session()
    t = s.query(Snapshot).filter_by(Snapshot.image.name==name).first()
    return t

def _ipv4_from_interface(interface):
    import socket
    from fcntl import ioctl
    from struct import pack
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SIOCGIFADDR = 0x8915
    try:
        return socket.inet_ntoa(ioctl(
            s.fileno(), SIOCGIFADDR, pack(
                "256s", interface.encode()
            )
        )[20:24])
    except OSError:
        return None
    finally:
        s.close()

class IPNet:

    def __init__(self, network_notation, bridge_ip=None, bridge_interface=None,
                 unique_ips=True):
        if "/" not in network_notation:
            network_notation = f"{network_notation}/24"

        self.network = ip_network(network_notation, strict=False)

        if bridge_ip:
            self.set_bridge_ip(bridge_ip)
        elif bridge_interface:
            self.set_bridge_interface(bridge_interface)
        else:
            self._bridge_ip = None

        if bridge_interface and bridge_ip:
            if_ip = _ipv4_from_interface(bridge_interface)
            if not if_ip:
                raise ValueError(
                    f"Bridge interface '{bridge_interface}' does not exist "
                    f"or does not have an IPv4 address."
                )
            if if_ip != bridge_ip:
                raise ValueError(
                    f"Bridge interface '{bridge_interface}' was expected to "
                    f"have IP: {bridge_ip}. It has {if_ip} instead."
                )

        self.bridge_interface = bridge_interface
        self._unique = unique_ips
        self._used = set()

    @property
    def netmask(self):
        return str(self.network.netmask)

    @property
    def bridge_ip(self):
        if not self._bridge_ip:
            self._bridge_ip = self.get_ips(count=1, start_offset=1)[0]

        return str(self._bridge_ip)

    def set_bridge_interface(self, interface_name):
        ip = _ipv4_from_interface(interface_name)
        if not ip:
            raise ValueError(
                f"Brige interface '{interface_name}' does not exist or does "
                f"not have an IPv4 address"
            )
        self.set_bridge_ip(ip)

    def bridge_exists(self):
        if self.bridge_interface:
            return _ipv4_from_interface(self.bridge_interface) is not None

        return False

    def check_ip_usable(self, ip):
        ip = ip_address(ip)
        if ip not in self.network:
            raise ValueError(
                f"{ip} is not part of network {self.network}"
            )

        if ip == self.network.broadcast_address:
            raise ValueError(
                f"IP is broadcast address of network: {self.network}"
            )

        if ip == self.network.network_address:
            raise ValueError(
                f"IP is network address of network: {self.network}"
            )

        if self._unique and not self._used:
            self._populate_used()

        if ip in self._used:
            raise KeyError(
                f"IP is already in use by another image, snapshot or "
                f"bridge in network {self.network}"
            )

    def set_bridge_ip(self, ip):
        bridge_ip = ip_address(ip)
        if bridge_ip not in self.network:
            raise ValueError(
                f"Bridge IP {bridge_ip} is not part of network {self.network}"
            )

        self._bridge_ip = bridge_ip

    def _populate_used(self):
        for ip, _ in find_used_ips():
            ip = ip_address(ip)
            if ip in self.network:
                self._used.add(ip)

    def get_ips(self, count=1, start_offset=1, start_ip=None):
        if start_ip:
            ip = ip_address(start_ip)
        else:
            ip = self.network.network_address + start_offset

        if ip not in self.network:
            raise ValueError(f"{ip} is not part of network {self.network}")

        if self._unique and not self._used:
            self._populate_used()

        ips = set()
        while len(ips) < count:
            curr_ip = ip
            ip = ip + 1
            if curr_ip in self._used or \
                    curr_ip == self.network.broadcast_address:
                continue

            if curr_ip not in self.network:
                raise KeyError(
                    f"Reached end of network {self.network}. Not enough room "
                    f"for {count} IPs. IPs left: {len(ips)}"
                )

            ips.add(curr_ip)

        self._used.update(ips)
        return [str(i) for i in ips]

    def __str__(self):
        return str(self.network)
