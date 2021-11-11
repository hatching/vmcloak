QEMU
====

This document describes how VMCloak supports QEMU. Follow the steps
in :ref:`qemu-networking` before getting started.

Currently all VMs are created with the ``-enable-kvm`` flag.

Dependencies:

* qemu 2.11 or higher. (tested with 4.2.1).
* qemu-system-x86
* qemu-utils
* qemu-system-common

Unsupported features:

* Shared directories
* Serial port
* VRAM size

.. _qemu-networking:

Networking (mandatory steps)
----------------------------

VMCloak creates QEMU VMs using the 'bridge' (`-netdev type=bridge`) network type. A single bridge interface with its
own subnet is needed for this. The interfaces that each VM needs are automatically created
by QEMU using the '`qemu-bridge-helper <https://wiki.qemu.org/Features/HelperNetworking>`_' binary.


The following steps must be performed so QEMU can automatically create and attach interfaces to an existing bridge.

1. Create a new bridge using the ``vmcloak-qemubridge`` tool. It must be run as root.

Its first argument is a name for a bridge. The second is the IP with in CIDR notation.
Use the ``-h/--help`` flags to get more information about this tool.

Run the tool to create a bridge interface.

.. code-block:: bash

    sudo vmcloak-qemubridge qemubr0 192.168.30.1/24

The bridge should exist after running this tool. Verify that it does.

.. code-block:: bash

    $ ip a show qemubr0
    8: qemubr0: <BROADCAST,MULTICAST,UP,LOWER_UP>
        link/ether ...
        inet 192.168.30.1/24 scope global qemubr0
           valid_lft forever preferred_lft forever

2. Find the location of the '`qemu-bridge-helper <https://wiki.qemu.org/Features/HelperNetworking>`_' binary and give a setuid bit so
it can be run as root by QEMU when non-root users use QEMU.

The helper is part of the `qemu-system-common` Ubuntu package. If available, it can often be found
at ``/usr/lib/qemu/qemu-bridge-helper`` or ``/usr/local/libexec/qemu-bridge-helper``.

.. code-block:: bash

   $ sudo chmod u+s <the path of qemu-bridge-helper>

3. Almost done. We now need to add our newly created bridge to the tool's ACL. It will not
create any interfaces otherwise.

The location of this ACL file depends on where the bridge helper is. The path is hardcoded in that binary.
It is most likely ``/etc/qemu/bridge.conf`` or ``/usr/local/etc/qemu/bridge.conf``.

A very ugly hack to find out is running:

.. code-block:: bash

    $ strings qemu-bridge-helper | grep "bridge.conf"

Add an ``allow <bridge name>`` entry to the file.
In this case our bridge is called: ``qemubr0``, so we add ``allow qemubr0``.


.. _qemu-vnc:

VNC
---

You can use the vrde/vrde-port options to enable VNC.
Note that QEMU adds an offset of 5900. If you specified port 0, it will be
5900, if you specify 1, it will be 5901, etc.
