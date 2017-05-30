
Installation on Linux
---------------------

.. contents::


1. Operating System needs
~~~~~~~~~~~~~~~~~~~~~~~~~

PyPlanet requires Python 3.5 and later. We also require to have some operating system libraries and build tools installed.
We will guide you through the steps that are required to install those requirements in this subtopic.

Debian / Ubuntu
```````````````

Install the operating system requirements by executing the following commands:

``sudo apt-get update && apt-get install build-essential libssl-dev libffi-dev python3-dev zlib1g-dev``

Fedora / RHEL based
```````````````````

Install the operating system requirements by executing the following commands:

``sudo yum install gcc libffi-devel python3-devel openssl-devel zlib``.


2. Install PyEnv and Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make things as easy as possible we are going to use `PyEnv`. It's a tool that will install Python for you with
all the requirements and also manage to adjust the environment we are running in.

The following steps are the same for all distributions.

.. note::

  Make sure you are logged in as the user that is going to run PyPlanet. (Mostly not root!).


**Install PyEnv**

.. code-block:: bash

  curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash
  printf '\nexport PATH="$HOME/.pyenv/bin:$PATH"\neval "$(pyenv init -)"\neval "$(pyenv virtualenv-init -)"\n' >> ~/.bashrc
  source ~/.bashrc

**Install Python**

.. code-block:: bash

  pyenv install 3.6.1
  pyenv global 3.6.1


.. attention::

  The first set of commands makes adjustments to the ``~/.bashrc`` file. It can be that you don't have this file installed.

  If that is the case, you can add those lines manually to any other script that is executed when you open your shell (``.profile``)
  or execute these commands manually at every start of a SSH session. Your SSH session might have to be restarted after this change!

  .. code-block:: bash

    export PATH="~/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"


.. _step-3-ref:

3. Create environment for your installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We recommend to separate multiple installations by creating a so called virtual environment. This will make sure you can
run several PyPlanet and dependency versions on the same Python installation. You can skip this step if you don't want to
use virtual environments, but we recommend to use it.

**Create virtualenv**:

.. code-block:: bash

    pyenv virtualenv 3.6.1 pyplanet
    # Where 'pyplanet' is your environment name, you need adjust this if you have multiple installations.

**Activate virtualenv**:

.. note::

  You have to activate your virtual environment **every time** you want to execute PyPlanet commands! That means that you have
  to activate before you update, start, develop and do anything with PyPlanet!

.. code-block:: bash

    pyenv activate pyplanet
    # Where 'pyplanet' is your environment name, you need adjust this if you have multiple installations.


4. PyPlanet Installation
~~~~~~~~~~~~~~~~~~~~~~~~

PyPlanet is published through the Python Package Index (PyPi) and is easy to install with ``pip``.

.. code-block:: bash

    pip install pyplanet --upgrade

After installing it on your system you can use the pyplanet cli commands. To get help about commands, use ``pyplanet help``.

5. Setup Project
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

To upgrade your existing installation, see our :doc:`Upgrading Guide </intro/upgrading>`.

.. warning::

  If you use the virtual environment we installed in :ref:`step-3-ref`, make sure you activate it **before you install or update dependencies**!


**Head to the next step**

Configure your PyPlanet installation now by going to the next chapter: :doc:`/intro/configuration`.
