Setup VMCloak
=============

Given VMCloak is available as a `Python Package
<https://pypi.python.org/pypi/vmcloak>`_ it features a ``setup.py`` for easy
installation. Besides of course installing VMCloak through ``pip`` using
``pip install -U vmcloak`` it is also possible to fetch the `Git repository
<https://github.com/jbremer/vmcloak>`_ and install the package globally
through ``sudo python setup.py install`` (or in a ``virtualenv`` through
``python setup.py install``).

Fetching the repository through Git allows one access to the latest
development version of VMCloak with features that may not have been pushed to
the Python Package yet. A full example of installing VMCloak manually can be
as follows:

.. code-block:: bash

    $ git clone git://github.com/jbremer/vmcloak
    $ cd vmcloak
    $ sudo python setup.py install

For development purposes you'll want to install it in development mode,
preferably inside of a ``virtualenv``:

.. code-block:: bash

    (venv)$ git clone git://github.com/jbremer/vmcloak
    (venv)$ cd vmcloak
    (venv)$ python setup.py develop
