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

For a quick walkthrough on the general usage of VMCloak, please refer to the
following blogpost: [http://jbremer.org/vmcloak3][blogpost].

[blogpost]: http://jbremer.org/vmcloak3

Credits
-------

The development of the VMCloak project initially started out as part of the
ITES Project at Avira, thanks to **Thorsten Sick**. Many thanks to
**Rasmus Männa** for lots of great contributions lately.

[![Coverage Status](https://coveralls.io/repos/github/jbremer/vmcloak/badge.svg)](https://coveralls.io/github/jbremer/vmcloak)
