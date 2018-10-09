# Copyright (C) 2014-2017 Jurriaan Bremer.
# Copyright (C) 2018 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os

from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, Text, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SCHEMA_VERSION = "5a5957711538"

conf_path = os.path.join(os.getenv("HOME"), ".vmcloak")
image_path = os.path.join(conf_path, "image")
vms_path = os.path.join(conf_path, "vms")
deps_path = os.path.join(conf_path, "deps")
iso_dst_path = os.path.join(conf_path, "iso")

repository = os.path.join(conf_path, "repository.db")
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
    paravirtprovider = Column(String(32))

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
    if not engine.dialect.has_table(engine, AlembicVersion.__tablename__):
        AlembicVersion.__table__.create(engine)

if not os.path.isdir(image_path):
    os.mkdir(image_path)

if not os.path.isdir(deps_path):
    os.mkdir(deps_path)

if not os.path.isdir(iso_dst_path):
    os.mkdir(iso_dst_path)
