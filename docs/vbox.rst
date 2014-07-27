VirtualBox
==========

As of this moment VMCloak only supports VirtualBox (i.e., no VMWare, KVM,
etc.)

VMCloak requires the hostonly interface ``vboxnet0`` in order to communicate
with the Virtual Machine. If ``vboxnet0`` is not yet running (VMCloak will
inform you about this), then :ref:`you have to create vboxnet0
<vbox-vboxnet0>`.

.. _vbox-vboxnet0:

Creating vboxnet0
-----------------

Executing the following two commands on the command line will create and start
the ``vboxnet0`` network:

.. code-block:: bash

    VBoxManage hostonlyif create
    VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1
