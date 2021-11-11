Configuration
=============

Since VMCloak 0.3 it no longer uses configuration files for simply creating
VMs. However, a couple of things remain necessary to be performed before
invoking VMCloak.

.. _conf-mounted-iso:

Mounting the ISO Image
----------------------

In order to mount a Windows Installer ISO image a directory should be created
with **root**, and then the image should be mounted on that directory, with
root as well. The following bash snippet depicts how to setup an ISO mount on
a Ubuntu/Debian system.

.. code-block:: bash

    mkdir /mnt/win10x64
    mount -o loop,ro win10x64.iso /mnt/win10x64

In order to mount an image under BSD the following commands might be required.

.. code-block:: bash

    mkdir /mnt/win10x64
    vnconfig /dev/vnd0d win10x64.iso
    mount -t cd9660 /dev/vnd0d /mnt/win10x64


.. _conf-serial-key:

Serial Key
----------

``--serial-key`` specifies the **serial key** to be used to install Windows in
the Virtual Machine. Although it is possible to randomize the serial key after
the installation has been finished, a valid serial key is required during
installation, and often times there is no *one serial key to rule them all*,
thus make sure to have a valid serial key at hand.

.. _conf-vmname:

VM Name
-------

The Virtual Machine name represents the unique identifier for this VM. This
value is the extra argument on the command line, e.g.,
``cuckoo1`` in ``vmcloak -s conf.ini cuckoo1``.

DNS Server
----------

By default the generated Virtual Machine will use Google's 8.8.8.8 and 8.8.4.4 DNS Servers.
This can be changed through ``--dns`` and ``--dns2``.

.. _conf-vm-visible:

Visible VM Generation
---------------------

The ``--vm-visible`` argument, if specified, runs the Virtual Machine in
**GUI** mode instead of **headless** mode (terms as per VirtualBox.) This
allows one to monitor the installation as it goes.

An installation might hang at the serial key dialog. This is the
case when the :ref:`conf-serial-key` provided is incorrect. At this point
VMCloak is unable to detect it when this happens.

**QEMU**

When using qemu the ``-display gtk`` argument is used to realize this.

**VNC**

Alternatively, on remote servers you might want to use VNC instead. Use ``--vrde`` to enable it and ``--vrde-port <port offset>`` to choose a port.
It will always listen on 0.0.0.0:5900+offset.



Semi-required configuration entries
-----------------------------------

A few configuration entries are not required, but should in most cases be
provided.

* :ref:`conf-hostonly-ip`
* :ref:`conf-hostonly-gateway`
* :ref:`conf-hostonly-mask`


.. _conf_guestnetwork:

Guest network
^^^^^^^^^^^^^

A network must be provided using the ``--network <some network address/cidr`` when creating a new image.
If no network is provided a default one for the chosen virtual machinery will be used. The IPs for images/snapshots can always
be looked up using ``vmcloak list images/snapshots``.

.. _conf-hostonly-ip:

Image IP address
^^^^^^^^^^^^^^^^

The IP address to assign to a new image is automatically chosen if none is given.
VMCloak picks the next available IP from the network provided by ``--network``.

It is still advised to provide VMCloak with an IP for an image so that it is
known to you from the start. The IP provided to the snapshot command is used as a first/start IP if multiple
snapshots have to be created.

.. _conf-hostonly-gateway:

Guest default gateway
^^^^^^^^^^^^^^^^^^^^^

VMCloak uses the IP of the provided bridge interface as the default gateway for the images and snapshots created from it.
This can be overridden by using the ``--gateway <an IP>`` argument.

.. _conf-hostonly-mask:

Guest network mask
^^^^^^^^^^^^^^^^^^

The network mask is automatically determined from the network given by the ``--network`` argument.

Suggested hardware/vm settings
------------------------------

Following are various configuration entries that are not necessary, but
allow one to do some custom modifications on the guest VM, which can be quite
useful if one needs to make a special VM for a custom analysis.

* :ref:`conf-ramsize`
* :ref:`conf-resolution`
* :ref:`conf-hdsize`

.. _conf-ramsize:

RAM Size
^^^^^^^^

With ``--ramsize`` one can specify the required RAM size of the VM in
megabytes. By default this value will be set to **2048** (which results to
2 GB of RAM). For Windows 7 and 10 should probably have at least 4GB of RAM.

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
all of the specified space at once. By default this value is set to 256 GB, but this does mean
that if at some point a VM really needs the 256 GB that the harddrive
shouldn't run out of space.

..
    .. _conf-keyboard-layout:

    Keyboard Layout
    ^^^^^^^^^^^^^^^

    By default the ``--keyboard-layout`` defaults to **US**. See
    :ref:`data-keyboard-layout` for a list of all available keyboard layouts.


Cuckoo Sandbox related
----------------------

Cuckoo 3 related information


.. _conf-cuckoo-tags:

Tags
^^^^

Cuckoo machines (VMs) can be assigned tags. These are small strings that identify specific characteristics about a VM.
An example of this is the installed software.

For example, if you install the *dotnet40* (.NET v4.0) and
*adobepdf* (Adobe PDF Reader) dependencies in your VM, then you might want to
represent this in its Cuckoo Sandbox tags.

When creating a snapshot with VMCloak, tags for installed software is added to the machine info JSON file.
Cuckoo reads this file when importing VMs using ``cuckoo machine import``.
