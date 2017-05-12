
Installation
------------

Requirements
~~~~~~~~~~~~

PyPlanet runs on Python 3.5 and later. Most linux distributions contain default packages or will come with Python
preinstalled. To be 100% sure you have to check if you have Python 3 and your version is above 3.5.

**Summary of requirements:**

* Python 3.5+ and pip 9+ (see bellow for upgrading pip).
* Virtualenv (see: http://pythoncentral.io/how-to-install-virtualenv-python/ )
* MySQL Server or PostgreSQL Server.
* Maniaplanet Dedicated MP4+, local or remote.

**Installing operating system requirements**

For some libraries, like crypto are some native libraries and build tools required.

* Ubuntu: ``sudo apt-get install build-essential libssl-dev libffi-dev python3-dev zlib1g-dev``
* Fedora/RHEL: ``sudo yum install gcc libffi-devel python3-devel openssl-devel zlib``.
* Windows: Run as Admin: ``pip install cryptography``

.. tip::

  If you still get errors with installing with pip, please take a look at: https://cryptography.io/en/latest/installation/#building-cryptography-on-linux

  If you are on Ubuntu 16.04 or later you can also use our wrapper bash script that automatically installs required os packages.

  ``bash <(curl -s https://raw.githubusercontent.com/PyPlanet/PyPlanet/master/docs/scripts/setup.sh)``


1. Check your Python and PIP version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all you have to check if your operating system has Python 3.5 or higher installed. To find out, type the following
commands in the command shell.

.. code-block:: bash

  python3 --version
  # OR
  python --version

The output should show this ``Python 3.5.2`` and the version number should be **3.5 or higher**!
If this is not the case you could check if your operating system has Python 3.5 support from it's package manager.
Ubuntu 16.04 and higher has Python 3.5, Debian 8 has no 3.5.

Windows, download Python 3.6 from the site: https://www.python.org/downloads/

**PyEnv**

If your operating system doesn't provide you 3.5 or higher, you have to use PyEnv. To install PyEnv execute the following
commands:

.. code-block:: bash

  # Execute this as the user you want to install PyPlanet for
  curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

After installing you would have to edit your ~/.bashrc file and add the following lines:

.. code-block:: bash

  export PATH="~/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"

Restart your SSH session right now to activate the PyEnv installation.

Next up is the installation of Python 3.6 with PyEnv, you can do this by executing the following shell commands.
This can take some time

.. code-block:: bash

  pyenv install 3.6.1


2. Virtual Environment for your installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We recommend using a `virtualenv` to install PyPlanet, and keep the version separate for multiple projects/dedicated servers.
With this method you won't have to upgrade all servers at the same time and don't have any issues with system managed python
packages.

In order to create a virtualenv you need to have the virtualenv tools installed. To install virtualenv, execute the following command:

**Using `virtualenv`**:

.. code-block:: bash

    # Ubuntu + Debian
    sudo apt-get install virtualenv

    # Generic Other Linux
    sudo -H pip install virtualenv

    # Windows (run cmd as administrator)
    pip install virtualenv

From now on you can create virtualenv environments.

.. code-block:: bash

    # Linux
    virtualenv -p python3 env

    # Windows:
    virtualenv -p [full path to python3 executable] env


From now you have to activate the virtualenv, every time you want to execute operations with PyPlanet (such as starting, installing, updating, etc).
To activate, use the following commands:

.. code-block:: bash

    # Linux
    source env/bin/activate

    # PyEnv
    pyenv activate pyplanet

    # Windows (cmd)
    env\Scripts\Activate.bat


**Using PyEnv**

With PyEnv it's slightly different, you have to create a virtualenv, but this virtualenv is not located in the same
folder as you are in now.

Create virtualenv with the following command:

.. code-block:: bash

  pyenv virtualenv 3.6.1 pyplanet
  # 3.6.1 = your installed python version
  # pyplanet = name you will give your virtualenv. Can be anything. remember it of course!

Activating the virtualenv is pretty easy with PyEnv:

.. code-block:: bash

  pyenv activate pyplanet
  # Where pyplanet is your virtualenv name.


3. PyPlanet Installation
~~~~~~~~~~~~~~~~~~~~~~~~

PyPlanet is published through the Python Package Index (PyPi) and is easy to install with ``pip``. **Make sure you activated
your virtualenv first!**

.. code-block:: bash

    # Install as root:
    pip install pyplanet -U

After installing it on your system you can use the pyplanet cli commands. To get help about commands, use ``pyplanet help``.

4. Setup Project
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
