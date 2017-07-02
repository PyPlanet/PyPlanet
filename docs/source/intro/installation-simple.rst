
Installation by Binary (Experimental)
-------------------------------------

.. error::

  **EXPERIMENTAL**: This method is new and can be unstable. Added since 0.5.0.

.. contents::


1. Downloading binary
~~~~~~~~~~~~~~~~~~~~~

Download the binary from the last GitHub release page: https://github.com/PyPlanet/PyPlanet/releases

Make sure you download the ``pyplanet.exe`` or ``pyplanet`` (depending if you have Windows or Linux).


2. Make binary excutable (Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This step is for Linux only!

You need to make sure you add the execution permission to the binary file.

.. code-block:: bash

  chmod +x pyplanet


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
