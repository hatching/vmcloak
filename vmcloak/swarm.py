# Copyright (C) 2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os
import yaml

from vmcloak.exceptions import SwarmError
from vmcloak.winxp import WindowsXP
from vmcloak.win7 import Windows7x64, Windows7x86
from vmcloak.win81 import Windows81x64, Windows81x86
from vmcloak.win10 import Windows10x64, Windows10x86

class Swarm(object):
    vms = {
        "winxp": {
            "isomount": WindowsXP.mount,
        },
        "win7x86": {
            "isomount": Windows7x86.mount,
            "serialkey": Windows7x86.dummy_serial_key,
        },
        "win7x64": {
            "isomount": Windows7x64.mount,
            "serialkey": Windows7x64.dummy_serial_key,
        },
        "win81x86": {
            "isomount": Windows81x86.mount,
            "serialkey": Windows81x86.dummy_serial_key,
        },
        "win81x64": {
            "isomount": Windows81x64.mount,
            "serialkey": Windows81x64.dummy_serial_key,
        },
        "win10x86": {
            "isomount": Windows10x86.mount,
            "serialkey": Windows10x86.dummy_serial_key,
        },
        "win10x64": {
            "isomount": Windows10x64.mount,
            "serialkey": Windows10x64.dummy_serial_key,
        },
    }

    def __init__(self, confpath):
        self.confpath = confpath
        self.machines = {}
        self.cfg = {}

    def load(self):
        """Reads, parses, interprets, and validates swarm configuration."""
        self.read_swarm()
        self.parse_matrix()
        self.interpret_machines()

    def read_swarm(self):
        """Reads swarm configuration."""
        if not os.path.exists(self.confpath):
            return

        try:
            cfg = yaml.load(open(self.confpath, "rb"))
        except yaml.YAMLError as e:
            raise SwarmError("Error reading swarm configuration: %s" % e)

        if not isinstance(cfg, dict):
            raise SwarmError("Swarm configuration should be a dictionary!")

        self.cfg = cfg

    def apply_dict(self, target, d):
        """Apply a dictionary to one or more elements."""
        if isinstance(target, list):
            for entry in target:
                entry.update(d)
            return target

        if isinstance(target, dict):
            target.update(d)
            return target

        raise SwarmError(
            "Invalid target type for applying a dictionary"
        )

    def parse_matrix(self):
        if not self.cfg.get("matrix"):
            raise SwarmError(
                "Build matrix is missing from swarm configuration!"
            )

        if isinstance(self.cfg["matrix"], dict):
            for name, machine in self.cfg["matrix"].items():
                if name in self.cfg:
                    raise SwarmError(
                        "Can't declare a VM name in the build matrix that "
                        "also exists as configuration entry: '%s'." % name
                    )

                self.machines[name] = self.parse_machine(name, machine)
                self.apply_dict(self.machines[name], machine)
        elif isinstance(self.cfg["matrix"], list):
            self.machines = self.parse_machines(self.cfg["matrix"])
        else:
            raise SwarmError("Build matrix should be a dictionary or list!")

    def parse_machines(self, machines):
        ret = {}
        for machine in machines:
            if machine not in self.cfg:
                raise SwarmError("Machine '%s' is not defined!" % machine)

            ret[machine] = self.parse_machine(machine, self.cfg[machine])
        return ret

    def parse_machine(self, machine, m):
        if "os" not in m:
            raise SwarmError(
                "Machine '%s' does not have an OS defined!" % machine
            )

        ret = {
            "os": m["os"],
        }

        if m["os"] in self.vms:
            ret.update(self.vms[m["os"]])
        else:
            ret.update(self.parse_machine(m["os"]))

        ret["deps"] = self.parse_dependencies(m.get("deps"), ret.get("deps"))
        return ret

    def parse_dependencies(self, deps, inherited):
        ret = []
        ret.extend(inherited or [])

        deps = deps or []
        if isinstance(deps, basestring):
            deps = deps.split()

        for dep in deps:
            if isinstance(dep, basestring):
                ret.append(self.parse_dependency(dep))
            elif isinstance(dep, dict):
                ret.append(self.apply_dict(
                    self.parse_dependency(dep.keys()[0]),
                    dep.values()[0][0]
                ))
            else:
                raise SwarmError()
        return ret

    def parse_dependency(self, dependency):
        if dependency not in self.cfg:
            raise SwarmError("Dependency '%s' not found!" % dependency)

        dep = self.cfg[dependency]
        if isinstance(dep, dict):
            dep = dep.items()
        elif isinstance(dep, list):
            dep = (None, dep),

        ret = []
        for requirement, info in dep:
            if requirement:
                if not requirement.startswith("os:"):
                    raise SwarmError(
                        "Currently only the os: requirement is allowed for "
                        "dependency criteria! Found: '%s'" % requirement
                    )

                target_os = requirement[3:]
            else:
                target_os = None

            if isinstance(info, basestring):
                ret.append({
                    "os": target_os,
                    "dependency": dependency,
                    "version": info,
                })
                continue

            if isinstance(info, list):
                for entry in info:
                    if isinstance(entry, dict):
                        ret.append(self.apply_dict({
                            "os": target_os,
                            "dependency": dependency,
                        }, entry))
                        continue

                    if isinstance(entry, (int, float, basestring)):
                        ret.append({
                            "os": target_os,
                            "dependency": dependency,
                            "version": "%s" % entry,
                        })
                        continue

                    raise SwarmError(
                        "Invalid dependency specification: %r" % info
                    )
                continue

            if isinstance(info, dict):
                ret.append(self.apply_dict({
                    "os": target_os,
                    "dependency": dependency,
                }, info))

        return ret

    def interpret_machines(self):
        """Interprets the machine configuration by removing incompatible
        dependencies."""
        for name, machine in self.machines.items():
            deps = []
            for dep in machine["deps"]:
                versions = []
                for version in dep:
                    if not version["os"] or version["os"] == machine["os"]:
                        versions.append(version)
                if versions:
                    deps.append(versions)
            machine["deps"] = deps
