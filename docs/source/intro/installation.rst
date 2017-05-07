
Installation
------------

Requirements
~~~~~~~~~~~~

PyPlanet runs on Python 3.5 and later. Most linux distributions contain default packages or will come with Python
preinstalled. To be 100% sure you have to check if you have Python 3 and your version is above 3.5.

**Summary of requirements:**

* Python 3.5+ and pip 9+
* Virtualenv (see: http://pythoncentral.io/how-to-install-virtualenv-python/ )
* MySQL Server or PostgreSQL Server.
* Maniaplanet Dedicated MP4+, local or remote.

.. note::

    If your OS does't have Python 3.5 or older provided. You could either compile Python for yourself or use PyEnv.
    Instructions on how to install PyEnv are in the github page <https://github.com/pyenv/pyenv-installer#github-way-recommended>.

    After installing you can install the desired python version with: ``pyenv install 3.6.1``.
    Also, you can't use `virtualenv` when using PyEnv. Use its alternative: ``pyenv virtualenv 3.6.1 pyplanet``

1. System (CLI) Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyPlanet is published through the Python Package Index (PyPi) and is easy to install with ``pip``. To install PyPlanet
on your system you need root rights. You can however install PyPlanet in the users pip context.

.. warning::::

    We don't recommend installing PyPlanet as root. Please use the ``--user`` parameter when installing the CLI tool.

.. code-block:: bash

    # Install as root:
    sudo -H pip install PyPlanet -U

    # Install in ~/.local
    pip --user install PyPlanet -U


After installing it on your system you can use the pyplanet cli commands. To get help about commands, use ``pyplanet help``.


2. Virtual Environment in your project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We recommend using a `virtualenv` to install PyPlanet, and keep the version separate for multiple projects/dedicated servers.
With this method you won't have to upgrade all servers at the same time and don't have any issues with system managed python
packages.

In order to create a virtualenv you need to have the virtualenv tools installed. To install virtualenv, execute the following command:

.. code-block:: bash

    # Linux
    sudo -H pip install virtualenv

    # Windows (run cmd as administrator)
    pip install virtualenv

From now on you can create virtualenv environments.

.. code-block:: bash

    # Linux + windows (cmd)
    virtualenv -p python3 env


From now you have to activate the virtualenv, every time you want to execute operations with PyPlanet (such as starting, installing, updating, etc).
To activate, use the following commands:

.. code-block:: bash

    # Linux
    source env/bin/activate

    # PyEnv
    pyenv activate pyplanet

    # Windows (cmd)
    env\Scripts\Activate.bat


2. Setup Project
~~~~~~~~~~~~~~~~

After installing PyPlanet on your system, you can't yet start any instances because starting requires you to give up an
settings module. You could either provide this with the start command or create a project directory with skeleton files.

We recommend using the ``init_project`` command to create a local project installation where you can install apps, keep
PyPlanet and it's apps up-to-date, provide settings through a useful settings module and provide ``manage.py`` as a wrapper
so you never have to manually provide your settings module.

In the example bellow we will setup a project with the name `canyon_server`. The folder `canyon_server` will be created
and skeleton files will be copied.

.. code-block:: bash

    pyplanet init_project canyon_server

After setup your project, you have to install or update your dependencies from your local ``requirements.txt``.
You should also use this command to **upgrade your installation**.

.. code-block:: bash

    pip install -r requirements.txt --upgrade

After setting up your project environment your ready to go the the next section bellow.

.. warning::

  If you use `virtualenv` or `pyenv`, make sure you activate it **before you install or update dependencies**!
