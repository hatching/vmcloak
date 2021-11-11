# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import json

import vmcloak.dependencies

class MachineConfDump:

    DEFAULT_NAME = "machineinfo.json"

    vmcloak_version = None
    machinery = None
    machinery_version = None

    def __init__(self, name, ip, agent_port, os_name, os_version,
                 architecture, tags=[], **kwargs):
        self.machine = {
            "name": name,
            "ip": ip,
            "agent_port": agent_port,
            "os_name": os_name,
            "os_version": os_version,
            "architecture": architecture,
            "tags": tags
        }
        self.machine.update(kwargs)

    def add_machine_field(self, key, value):
        self.machine[key] = value

    def tags_from_image(self, image):
        all_tags = []
        for depname, _ in image.installed:
            try:
                tags = vmcloak.dependencies.names[depname].tags
            except KeyError:
                continue

            if not tags:
                continue

            if isinstance(tags, str):
                all_tags.append(tags)
            else:
                for tag in tags:
                    all_tags.append(tag)

        self.machine["tags"] = list(set(all_tags))

    def write_dump(self, path):
        dump = {
            "vmcloak_version": self.vmcloak_version,
            "machinery": self.machinery,
            "machinery_version": self.machinery_version,
            "machine": self.machine
        }
        with open(path, "w") as fp:
            json.dump(dump, fp, indent=2)
