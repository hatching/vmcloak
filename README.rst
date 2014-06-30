VMCloak
=======

Automated Virtual Machine Generation and Cloaking for Cuckoo Sandbox.

Introduction
------------

VMCloak is a tool to fully create and prepare Virtual Machines that can be
used by Cuckoo Sandbox. In order to create a new Virtual Machine one should
prepare a few configuration values that will be used later on by the tool.

Dependencies
------------

VMCloak relies on a couple of tools and libraries that are required during
the process of generating a new VM.

* Python 2.6+
* mkisofs/genisoimage
* VirtualBox

Usage
-----

In order to run the tool you'll have to provide all the required configuration
variables that can be found when running ``./vmcloak.py -h``. Optionally one
can generate a configuration file with various default values (such as path
of Cuckoo Sandbox and `basedir`) and load these settings using the `-s` flag.

Credits
-------

Without the help of `nLite <http://www.nliteos.com/>`_ this tool would
probably not have been as complete as it is now. Inspiration on how to design
the output ISO files has for a large part been derived from changes observed
by `nLite`.
