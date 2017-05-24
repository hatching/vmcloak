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

Installation
------------

On Ubuntu a few packages are required due to the indirect inclusion of the
``cryptography`` Python package. Installation of all packages *excluding*
``VirtualBox`` may be done by running as follows.

```bash
$ sudo apt-get install build-essential libssl-dev libffi-dev
$ sudo apt-get install python-dev genisoimage
$ sudo pip install vmcloak
```

Or one may also install it in a virtualenv.

```bash
$ virtualenv .
$ source ./bin/activate
$ pip install -U vmcloak
```

Usage
-----

For a quick walkthrough on the general usage of VMCloak, please refer to the
following blogpost: [http://jbremer.org/vmcloak3][blogpost].

[blogpost]: http://jbremer.org/vmcloak3

Testing
-------

In order to run the VMCloak unit tests, which should be run on a custom build
server due to its huge resource requirements (i.e., setting up multiple
virtual machines is not something to take lightly), we provide some pointers
for setting up such an environment.

First of all, the _~/.vmcloak/config.json_ should be created containing a JSON
blob with, currently, one value. The _winxp.serialkey_ value should be
featured with a serial key that matches your Windows XP ISO file. An example
config.json file may look as follows.

```javascript
{
    "winxp": {
        "serialkey": "windows xp serial key here"
    }
}
```

Then install _pytest_ and _pytest-xdist_:

```bash
$ pip install -U pytest pytest-xdist
```

Mount all of the ISO files as required, for a default configuration this looks
as follows (the following commands should be run as _root_ user):

```bash
$ mkdir /mnt/winxp
$ mount -o loop,ro vms/winxppro.iso /mnt/winxp

$ mkdir /mnt/win7x64
$ mount -o loop,ro vms/win7ultimate.iso /mnt/win7x64

$ mkdir /mnt/win81x64
$ mount -o loop,ro vms/Win8.1_EnglishInternational_x64.iso /mnt/win81x64

$ mkdir /mnt/win10x64
$ mount -o loop,ro vms/Win10_1511_2_EnglishInternational_x64.iso /mnt/win10x64
```

Now we're going to run the actual unit tests. Note that we can speed them up
by specifying N unit tests to be ran in parallel. As most of the tests
actually install Windows or run a virtual machine, we recommend to run at most
one unit test per CPU core. Also reserve about two to four gigabytes of RAM
for each extra unit test in parallel. E.g., if you want to run four unit tests
in parallel, then your computer should have at least four CPU cores and 16GB
of RAM.

Finally run the unit tests:

```bash
py.test -n 8
```

Credits
-------

The development of the VMCloak project initially started out as part of the
ITES Project at Avira, thanks to **Thorsten Sick**. Many thanks to
**Rasmus Männa** for lots of great contributions lately.

[![Coverage Status](https://coveralls.io/repos/github/jbremer/vmcloak/badge.svg)](https://coveralls.io/github/jbremer/vmcloak)
