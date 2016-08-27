# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import io
import logging
import os.path
import random
import requests

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

class Wallpaper(Dependency):
    name = "wallpaper"

    doges = [
        "https://cuckoo.sh/vmcloak/doge1.jpg",
        "https://cuckoo.sh/vmcloak/doge2.jpg",
        "https://cuckoo.sh/vmcloak/doge3.jpg",
    ]

    def init(self):
        self.filepath = None

    def run(self):
        uploadpath = os.path.join(
            self.a.environ("USERPROFILE"), "Pictures", "wall.jpg"
        )

        if not self.filepath:
            f = io.BytesIO(requests.get(random.choice(self.doges)).content)
        else:
            f = open(self.filepath, "rb")

        self.a.upload(uploadpath, f)

        # Add Wallpaper in registry.
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Control Panel\\Desktop\" "
            "/v Wallpaper /t REG_SZ /d  %s /f" % uploadpath
        )
