# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency

class ThreemonPatch(Dependency):
    name = "threemonpatch"
    tags = ["threemonpatch"]

    exes = [
        {
            "arch": "amd64",
            "urls": [
                "https://hatching.dev/hatchvm/patchandgo_amd64_vmcloak.exe",
            ],
            "sha1": "a8f8ed626b9fc9f66938ac034db4e8750664a6ac",
        }]

    def run(self):
        self.upload_dependency("C:\\patchandgo.exe")
        self.a.execute("C:\\patchandgo.exe")
        self.a.remove("C:\\patchandgo.exe")
