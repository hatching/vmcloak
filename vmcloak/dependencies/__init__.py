# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

from vmcloak.abstract import Dependency
from vmcloak.misc import import_plugins

plugins = import_plugins(__file__, "vmcloak.dependencies", globals(), Dependency)
names = dict((plugin.name, plugin) for plugin in plugins)
