.. _hwconfig:

Hardware Configuration
======================

Through hardware profiles VMCloak is able to cloak the names, versions, etc
of the various hardware components that the Virtual Machine software is
emulating.

.. _hwconfig-create:

Creating a Hardware Profile
---------------------------

Creating a new hardware profile of a machine requires one to run
``vmcloak-gethwconf <profile>`` on said machine. The ``profile`` represents
the name of this profile - the profile will be called after it and put in the
``hwconf/`` directory.

As an example, to create a hardware profile of a lenovo thinkpad, one may do:

.. code-block:: bash

    vmcloak-gethwconf lenovo_x220
