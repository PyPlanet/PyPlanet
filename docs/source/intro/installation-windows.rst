
Installation on Windows
-----------------------

.. contents::


1. Installing Python
~~~~~~~~~~~~~~~~~~~~

If you have not yet installed Python 3.5 or later on your Windows machine, do it now by going to the following link:

https://www.python.org/downloads/release/python-361/

Head towards the end of the page and click on the `Windows x86-64 executable installer` link. After starting the executable
you will get an wizard.

Make sure it looks like this and click on the red area to continue.


.. figure:: /_static/intro/python-windows-1.png
  :alt: Setup wizard with the required settings

  Setup wizard with the checkboxes enabled.

.. note::

  Make sure you checked the two checkboxes: `Install launcher for all users` and `Add Python to PATH`.


2. Creating Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To prevent the usage of the administration leverage and to benefit from multiple PyPlanet installations and a clean environment
we recommend to setup a Virtual Environment.

First of all we need to install the ``virtualenv`` package. To do so, open a terminal screen by hitting start and write cmd. Open the command prompt.

.. code-block:: bash

  pip install virtualenv


After this we will initiate the environment, you can do this by going to your directory where you want to setup the PyPlanet installation.
Create a folder somewhere that is empty and ready for the PyPlanet settings and other files.

Open a terminal in this folder by holding :kbd:`SHIFT` and :kbd:`Right click` on an empty space in the folder. Then click ``Open terminal here``.

In the terminal, type the following command to create the environment:

.. code-block:: bash

  virtualenv env


From now you have to activate the virtualenv, every time you want to execute operations with PyPlanet (such as starting, installing, updating, etc).
To activate, use the following commands:

.. code-block:: bash

  # Windows, in your command prompt
  env\Scripts\activate.bat


3. PyPlanet Installation
~~~~~~~~~~~~~~~~~~~~~~~~

PyPlanet is published through the Python Package Index (PyPi) and is easy to install with the ``pip`` commands.

.. code-block:: bash

  pip install pyplanet --upgrade

After installing it on your system you can use the pyplanet cli commands. To get help about commands, use ``pyplanet help``.

4. Setup Project
~~~~~~~~~~~~~~~~

After installing PyPlanet on your system, you can't yet start any instances because starting requires you to give up an
settings module. You could either provide this with the start command or create a project directory with skeleton files.

We recommend using the ``init_project`` command to create a local project installation where you can install apps, keep
PyPlanet and it's apps up-to-date, provide settings through a useful settings module and provide ``manage.py`` as a wrapper
so you never have to manually provide your settings module.

Because you have created an Virtual Environment earlier you want to store your 'project' in the same folder. You can do this
with the following command:

.. code-block:: bash

  pyplanet init_project .

After setup your project, you have to install or update your dependencies from your local ``requirements.txt``.

To upgrade your existing installation, see our :doc:`Upgrading Guide </intro/upgrading>`.

.. warning::

  If you use the virtual environment we installed in :ref:`step-3-ref`, make sure you activate it **before you install or update dependencies**!


**Head to the next step**

Configure your PyPlanet installation now by going to the next chapter: :doc:`/intro/configuration`.
