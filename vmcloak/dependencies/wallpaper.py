# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

class Wallpaper(Dependency):
    name = "wallpaper"

    def init(self):
        self.filepath = None

    def check(self):
        if not self.filepath or not os.path.isfile(self.filepath):
            log.error("Please provide wallpaper png file to upload.")
            return False

    def run(self):
        uploadpath = os.path.join(self.a.environ("USERPROFILE"), "Pictures", "wall.jpg")

        self.upload_dependency(uploadpath, self.filepath)
        
        # add Wallpaper in registry 
        self.a.execute(
            "reg add \"HKEY_CURRENT_USER\\Control Panel\\Desktop\" "
            "/v Wallpaper /t REG_SZ /d  %s /f" % uploadpath
        )