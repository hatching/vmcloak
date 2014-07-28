.. toctree::
   :hidden:

   kblayout


Configuration
=============

VMCloak takes a configuration file and/or command line arguments as input,
and generates the Virtual Machine as output. Naturally this process includes
a whole lot of steps, thus the configuration allows one to tweak as many steps
as possible.

Ini file
--------

As it is not uncommon for one to create multiple VMs at once, rather than just
a single one, VMCloak supports one or more configuration file(s) to be
specified using the ``-s`` (short for ``--settings``) switch.

Configuration entries in the INI files should be present in the ``vmcloak``
section. E.g., ``vmcloak --basedir ~/vms`` would be equal to having the
following INI file, *conf.ini*, with ``vmcloak -s conf.ini``.

.. code-block:: ini

    [vmcloak]
    basedir = ~/vms

Configuration order
-------------------

VMCloak features default values for various configuration values. These
defaults may be overwritten through settings files as well as parameters on
the command line.

Let's take the following command:

.. code-block:: bash

    vmcloak -s first.conf -s second.conf --iso-mount /mnt/winxp cuckoo1

In this example the order of precedence is as follows (from lowest to
highest):

* Default values.
* The ``first`` settings file.
* The ``second`` settings file.
* Command line arguments.

As usual, if a particular value is set twice, the value with the highest
precedence is used in the end. E.g., if ``first.conf`` set ``--iso-mount``,
then this value is overwritten by the command line in this case.

Required configuration entries
------------------------------

A few configuration entries are required.

* :ref:`conf-mounted-iso`
* :ref:`conf-basedir`
* :ref:`conf-serial-key`
* :ref:`conf-vmname`

.. _conf-mounted-iso:

Mounted ISO Image
^^^^^^^^^^^^^^^^^

``--iso-mount`` reflects one of the most important configuration entries.
``--iso-mount`` accepts a path to a **mounted** Windows Installer ISO image.
In order to mount a Windows Installer ISO image a directory should be created
with **root**, and then the image should be mounted on that directory, with
root as well. The following bash snippet depicts how to setup the ISO mount.

.. code-block:: bash

    sudo mkdir /mnt/winxp
    sudo mount -o loop,ro winxp.iso /mnt/winxp

Then, when mounted, one would give ``--iso-mount /mnt/winxp`` to ``vmcloak``.

.. _conf-basedir:

Base Directory
^^^^^^^^^^^^^^

``--basedir`` specifies the path to the base directory where a directory will
be created for the Virtual Machine. The directory will contain files such as
the machine information, snapshots, the ISO disk image, and the *harddrive*
image.

.. _conf-serial-key:

Serial Key
^^^^^^^^^^

``--serial-key`` specifies the **serial key** to be used to install Windows in
the Virtual Machine. Although it is possible to randomize the serial key after
the installation has been finished, a valid serial key is required during
installation, and often times there is no *one serial key to rule them all*,
thus make sure to have a valid serial key at hand.

.. _conf-vmname:

VM Name
^^^^^^^

The Virtual Machine name represents the unique identifier for this VM. This
value is the extra argument on the command line, e.g.,
``cuckoo1`` in ``vmcloak -s conf.ini cuckoo1``.

Semi-required configuration entries
-----------------------------------

A few configuration entries are not required, but should in most cases be
provided.

* :ref:`conf-hostonly-ip`
* :ref:`conf-dependencies`

.. _conf-hostonly-ip:

Guest hostonly IP address
^^^^^^^^^^^^^^^^^^^^^^^^^

By default Guest ``--hostonly-ip`` address defaults to ``192.168.56.101``,
which is perfectly fine when one only intends to create one VM. However, if
one wants to create multiple VMs, then the static IP addresses should be
unique. Normally one would start counting at ``192.168.56.101`` to
``192.168.56.102``, ``192.168.56.103``, etc.

.. _conf-dependencies:

Dependencies
^^^^^^^^^^^^

``--dependencies`` accepts a *comma-separated* list of 3rd party software
packages that should be installed automatically in the VM. These packages
allow one to quickly and easily install commonly used software, such as, the
.NET framework, Adobe PDF Reader, Firefox, Chrome, Microsoft Office, etc.

As VMCloak has its `own repository for these packages
<https://github.com/jbremer/vmcloak-deps>`_ it is quite likely that one will
run into a piece of software which is not in the dependency repository yet.
In that case, please take a look at :ref:`deps-create` to make your own and
:ref:`deps-submit`, or alternatively :ref:`deps-request`.

Suggested configuration entries
-------------------------------

Following are various configuration entries that are not necessary, but
allow one to do some custom modifications on the guest VM, which can be quite
useful if one needs to make a special VM for a custom analysis.

* :ref:`conf-ramsize`
* :ref:`conf-resolution`
* :ref:`conf-hdsize`
* :ref:`conf-hwvirt`
* :ref:`conf-keyboard-layout`

.. _conf-ramsize:

RAM Size
^^^^^^^^

With ``--ramsize`` one can specify the required RAM size of the VM in
megabytes. By default this value will be set to **1024mb**.

.. _conf-resolution:

Resolution
^^^^^^^^^^

``--resolution`` sets the resolution of the VM. By default the resolution
will be set to **1024x768**, a not too uncommon resolution if your PC was
bought in the year 2006.

.. _conf-hdsize:

Harddrive Size
^^^^^^^^^^^^^^

``--hdsize`` allows one to specify the harddrive size of the VM in megabytes.
As the created harddrive is enlarged in size on-demand, rather than allocating
all of the specified space at once, it doesn't really matter whether one puts
32 GB or 256 GB. By default this value is set to 256 GB, but this does mean
that if at some point a VM really needs the 256 GB that the harddrive
shouldn't run out of space.

.. _conf-hwvirt:

Hardware Virtualization
^^^^^^^^^^^^^^^^^^^^^^^

If one hasn't enabled **VT-x** in the BIOS then it is not possible to use
hardware virtualization. If one gets such error, then provide ``--no-hwvirt``.
To explicitly enable hardware virtualization provide ``--hwvirt``.

.. _conf-keyboard-layout:

Keyboard Layout
^^^^^^^^^^^^^^^

By default the ``--keyboard-layout`` defaults to **US**. See
:ref:`data-keyboard-layout` for a list of all available keyboard layouts.

Cuckoo Sandbox configuration entries
------------------------------------

These configuration entries are related to direct interaction with Cuckoo
Sandbox as VMCloak has the ability to automatically add the created VM to
Cuckoo Sandbox.

* :ref:`conf-cuckoo-directory`
* :ref:`conf-cuckoo-tags`
* :ref:`conf-no-register-cuckoo`

.. _conf-cuckoo-directory:

Cuckoo Directory
^^^^^^^^^^^^^^^^

In order to add a created VM automatically to Cuckoo Sandbox one must run a
recent version of Cuckoo Sandbox (**1.2-dev** or higher) which ships the
``./utils/machine.py`` utility script. The ``--cuckoo`` argument accepts a
path to the root of your Cuckoo Sandbox setup to interact with Cuckoo Sandbox.

.. _conf-cuckoo-tags:

Tags
^^^^

Optionally ``--tags`` adds tags for the created VM when registering it with
Cuckoo Sandbox. For example, if you install the *dotnet40* (.NET v4.0) and
*adobepdf* (Adobe PDF Reader) dependencies in your VM, then you might want to
represent this in its Cuckoo Sandbox tags as ``dotnet,adobe`` or something
like this. For more information on tags, see
`the official Cuckoo Sandbox documentation
<http://docs.cuckoosandbox.org/en/latest/usage/submit/?highlight=tags>`_.

.. _conf-no-register-cuckoo:

No Register Cuckoo
^^^^^^^^^^^^^^^^^^

If the ``--cuckoo`` argument is not provided, or it is provided but the
created VM should not be registered with Cuckoo Sandbox, then the
``--no-register-cuckoo`` argument allows one to do that.

Debugging configuration entries
-------------------------------

As is there's not much debugging one can do. This limits one to *visual*
debugging as described as per :ref:`conf-vm-visible`.

.. _conf-vm-visible:

Visible VM Generation
^^^^^^^^^^^^^^^^^^^^^

The ``--vm-visible`` argument, if specified, runs the Virtual Machine in
**GUI** mode instead of **headless** mode (terms as per VirtualBox.) This
allows one to monitor the installation as it goes.

Often times the installation will hang at the serial key dialog. This is the
case when the :ref:`conf-serial-key` provided is incorrect. At this point
VMCloak is unable to detect it when this happens.
