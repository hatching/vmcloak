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

In order to run VMCloak you'll at the very least require the following:

* Python 3.6 or higher.
* mkisofs *or* genisoimage.
* QEMU 2.11 or higher (tested with 4.2.1).
* **root** access to mount images and perform actions such as creating network bridges.


Installation
------------

It is recommended that VMCloak is installed in a Virtualenv and on the user
that should own the created virtual machines.

VMCloak is available as a [Python Package](<https://pypi.python.org/pypi/vmcloak>)
It can be installed with ``pip`` using ``pip install -U vmcloak``.

Install the requirements. See the docs/ for a full list of requirements.

```bash
$ sudo apt update
$ sudo apt install python3 genisoimage qemu-system-x86 qemu-utils qemu-system-common
```


It is recommended to install VMCloak in a virtualenv.

```bash
$ virtualenv venv
$ source venv/bin/activate
$ (venv) pip install -U vmcloak
```

Fetching the [Git repository](<https://github.com/hatching/vmcloak>)  through allows one access to the latest
development version of VMCloak with features that may not have been pushed to
the Python Package yet. A full example of installing VMCloak manually can be
as follows:

```bash
$ (venv) git clone https://github.com/hatching/vmcloak.git
$ (venv) cd vmcloak
$ (venv) pip install .
```

Docs
----

```bash
$ (venv) pip install -e .[docs]
$ (venv) cd docs
$ (venv) make html
$ (venv) <your browser>/_build/html/index.html
```

<!--
Usage
-----

For a quick walkthrough on the general usage of VMCloak, please refer to the
following blogpost: [http://jbremer.org/vmcloak3][blogpost].

[blogpost]: http://jbremer.org/vmcloak3

--->
<!---
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
--->
Credits
-------

The development of the VMCloak project initially started out as part of the
ITES Project at Avira, thanks to **Thorsten Sick**. Many thanks to
**Rasmus Männa** for lots of great contributions lately.


<!---
[![Coverage Status](https://coveralls.io/repos/github/jbremer/vmcloak/badge.svg)](https://coveralls.io/github/jbremer/vmcloak)
--->
