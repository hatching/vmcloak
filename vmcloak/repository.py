# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os

from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

conf_path = os.path.join(os.getenv("HOME"), ".vmcloak")
image_path = os.path.join(conf_path, "image")
vms_path = os.path.join(conf_path, "vms")
deps_path = os.path.join(conf_path, "deps")

repository = os.path.join(conf_path, "repository.db")
engine = create_engine("sqlite:///%s" % repository)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Image(Base):
    """Represents each image that is created and altered along the way."""
    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    mode = Column(String(16))
    name = Column(String(64))
    path = Column(Text)
    osversion = Column(String(32))
    servicepack = Column(String(32))
    ipaddr = Column(String(32))
    port = Column(Integer)
    adapter = Column(String(32))
    netmask = Column(String(32))
    gateway = Column(String(32))

class Snapshot(Base):
    """Represents each snapshot that has been created."""
    __tablename__ = "snapshot"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("image.id"))
    vmname = Column(String(64))
    ipaddr = Column(String(32))
    port = Column(Integer)
    hostname = Column(String(32))

if not os.path.isdir(conf_path):
    os.mkdir(conf_path)

Base.metadata.create_all(engine)

if not os.path.isdir(image_path):
    os.mkdir(image_path)

if not os.path.isdir(deps_path):
    os.mkdir(deps_path)
