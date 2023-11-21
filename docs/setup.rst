Setup VMCloak
=============

It is recommended that VMCloak is installed in a Virtualenv and on the user
that should own the created virtual machines.

.. Attention::
   Do not use the PyPI-version of VMCloak. It is outdated and heavily bugged.

Fetching the `Git repository <https://github.com/Cryss76/vmcloak>`_ is the way to go.
There you get the latest working version with the least bugs.
A full example of installing VMCloak manually can be
as follows:

.. code-block:: bash

    $ git clone https://github.com/Cryss76/vmcloak.git
    $ cd vmcloak
    $ pip install .

For development purposes you'll want to install it in development mode,
preferably inside of a ``virtualenv``:

.. code-block:: bash

    (venv)$ git clone https://github.com/Cryss76/vmcloak.git
    (venv)$ cd vmcloak
    (venv)$ pip install -e .
