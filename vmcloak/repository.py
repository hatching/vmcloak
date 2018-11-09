# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
from sys import modules
from os.path import join, exists
from json import load

from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

conf_path = join(os.getenv("HOME"), ".vmcloak")
image_path = join(conf_path, "image")
vms_path = join(conf_path, "vms")
deps_path = join(conf_path, "deps")
iso_dst_path = join(conf_path, "iso")

repository = join(conf_path, "repository.db")
engine = create_engine("sqlite:///%s" % repository)
Base = declarative_base()
Session = sessionmaker(bind=engine)

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

    @property
    def platform(self):
        return platform(self.vm)

    def VM(self):
        return platform(self.vm).VM(self.name)

    def attr(self):
        translate = {"ipaddr": "ip"}
        attr = {}
        for k in ("path", "osversion", "servicepack", "ipaddr", "port",
                  "adapter", "netmask", "gateway", "cpus", "ramsize",
                  "vramsize"):
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

    @property
    def platform(self):
        return platform(self.image.vm)

    def VM(self):
        return platform(self.image.vm).VM(self.vmname)

if not os.path.isdir(conf_path):
    os.mkdir(conf_path)

Base.metadata.create_all(engine)

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
