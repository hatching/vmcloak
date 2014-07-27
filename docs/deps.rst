Dependencies
============

VMCloak features various dependencies. These dependencies allow one to install
critical and/or useful software packages in the Virtual Machine without any
user interaction. For example, to run Cuckoo Python is required, and to run
.NET applications the .NET framework is required.

For a list of all available extensions, please refer to
:ref:`deps-available`. If you find yourself requiring a package that is not
yet supported, then you can either :ref:`create a new dependency yourself
<deps-create>` and :ref:`submit the dependency <deps-submit>` or
:ref:`request a new dependency <deps-request>`.

.. _deps-create:

Creating new Dependencies
-------------------------

To add a new dependency a few basic steps have to be taken:

* Add the installer to the ``files/`` directory of the ``vmcloak-deps``
  repository. (The ``vmcloak`` repository clones the ``vmcloak-deps``
  repository into the ``deps/`` directory.)
* Create a new section in ``vmcloak-deps``'s ``repo.ini``. The name of the
  section will become the alias of the new dependency:

  .. code-block:: ini

      [alias]

* Every dependency requires at least some basic information:

  * ``filename``: the filename of the installer
  * ``description``: the description of this dependency

  .. code-block:: ini

      [alias]
      filename = installer.exe
      description = Installer of Application X

* If this dependency depends on one or more other dependencies (e.g.,
  an imaginary Paint.NET dependency depends on the .NET dependency), then we
  have to add the alias for each of these dependencies to the ``dependencies``
  attribute:

  .. code-block:: ini

      [alias]
      filename = installer.exe
      description = Installer of Application X
      dependencies = dotnet40 python27

* If the installer requires any arguments on the command line then there's
  the ``arguments`` attribute. E.g., to install the .NET framework dependency
  without any user interaction the ``/passive`` and ``/norestart`` arguments
  are required on the command line (following is the actual ``dotnet40``
  dependency):

  .. code-block:: ini

      [dotnet40]
      filename = dotNetFx40_Full_x86_x64.exe
      dependencies = wic
      description = .NET v4.0
      arguments = /passive /norestart

* Some depedencies may already have been installed on the Virtual Machine. In
  that case it might be useful to check whether this is the case and abort if
  so. Using the ``marker`` attribute you can check whether a particular file
  is already present:

  .. code-block:: ini

      [wic]
      filename = wic_x86_enu.exe
      description = Windows Imaging Component
      arguments = /passive /norestart
      marker = c:\windows\system32\windowscodecs.dll


* If it is required to run one or more commands after the installer has
  finished then ``cmd<N>`` starting at ``0`` up to ``N`` can be used. E.g.,
  the Python 2.7 package requires to manually click through a couple of
  screens in the installer:

  .. code-block:: ini

      [python27]
      filename = python-2.7.6.msi
      flags = background
      description = Python 2.7.6
      cmd0 = click.exe "Python 2.7.6 Setup" "Next >"
      cmd1 = click.exe "Python 2.7.6 Setup" "Next >"
      cmd2 = click.exe "Python 2.7.6 Setup" "Next >"
      cmd3 = click.exe "Python 2.7.6 Setup" "Finish"

* In the ``cmd<N>`` example we've also already seen the ``flags`` attribute.
  Following are the supported flags:

  * ``background``: run the installer in the background (allows executing
    other commands while running the installer, such as happens in the Python
    package.)

Using the new Dependency
^^^^^^^^^^^^^^^^^^^^^^^^

Having followed all these steps your dependency should be good to go. Now add
the alias of the newly created dependency to the list of ``--dependencies``
when calling ``./vmcloak.py``.

.. _deps-submit:

Submit a new Dependency
-----------------------

It is, naturally, possible to include your dependencies upstream, and you're
very much encouraged to do so! The easiest way to submit a dependency is to
`fork the vmcloaks-deps repository
<https://help.github.com/articles/fork-a-repo>`_, :ref:`create a commit with
the new dependency <deps-commit>`, and `creating a pull request on github
<https://help.github.com/articles/creating-a-pull-request>`_.

.. _deps-commit:

Creating a commit for the Dependency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're installer is called ``installer.exe`` then it should look pretty
much like the following:

.. code-block:: bash

    # Add the files.
    git add -f files/installer.exe repo.ini

    # Commit the files.
    git commit -m "Added dependency X."

    # Push the commit.
    git push

.. _deps-request:

Request a new Dependency
------------------------

If you're missing a dependency, but you don't know how to make a new
dependency yourself, then you can always ask if somebody would like to make
one for you.

To do this, please `make a new issue on Github
<https://github.com/jbremer/vmcloak-deps/issues/new>`_.

.. _deps-available:

Available Dependencies
----------------------

.. program-output:: ../utils/depslist.py
