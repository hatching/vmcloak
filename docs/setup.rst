Setup VMCloak
=============

It is recommended that VMCloak is installed in a Virtualenv and on the user
that should own the created virtual machines.

VMCloak is available as a `Python Package <https://pypi.python.org/pypi/vmcloak>`_
It can be installed with ``pip`` using ``pip install -U vmcloak``.


Fetching the `Git repository <https://github.com/hatching/vmcloak>`_  through allows one access to the latest
development version of VMCloak with features that may not have been pushed to
the Python Package yet. A full example of installing VMCloak manually can be
as follows:

.. code-block:: bash

    $ git clone git@github.com:hatching/vmcloak.git
    $ cd vmcloak
    $ pip install .

For development purposes you'll want to install it in development mode,
preferably inside of a ``virtualenv``:

.. code-block:: bash

    (venv)$ git clone git@github.com:hatching/vmcloak.git
    (venv)$ cd vmcloak
    (venv)$ pip install -e .
