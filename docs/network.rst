Networking
==========

By default, and at the moment this is necessary for VMCloak to work, every
generated Virtual Machine will have a hostonly network adapter. This adapter
is used to talk to Cuckoo. However, as it is host-only, this does not allow
the Virtual Machine to reach the internet.

In case you'd like the Virtual Machine to be able to have full access to the
internet then that's also possible of course. However, do take into account
that this indirectly allows **malware to abuse your internet connection**.

There are multiple approaches to getting networking inside the Virtual
Machines working - following is the easiest approach. (Other approaches
include, but are not limited to, a bridged network adapter, a NAT network,
etc.)

Full-internet access
--------------------

In order to setup full internet access for Virtual Machines the following two
steps will be taken. **Note that these steps can also be taken after
generating the Virtual Machines hence magically giving them internet access.**

* Setup hostonly network interface
* Run a bash script around iptables(8)

To start off :ref:`setup a hostonly interface for VirtualBox <vbox-vboxnet0>`.
Then run the following bash script as **root**. For your convenience it can
be found on your system by running ``vmcloak-iptables`` (the name of this
script is subject to change in the future, though.)

.. literalinclude:: ../bin/vmcloak-iptables
    :language: python

That being said setting up full internet access for your Virtual Machines
boils down to running the following commands:

.. code-block:: bash

    VBoxManage hostonlyif create
    VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1
    sudo vmcloak-iptables
