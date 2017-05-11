|
|
|
|
|
|

Upgrading PyPlanet
==================

Upgrading an existing installation isn't difficult at all. The only thing you really need to be careful about is the
breaking changes.

Before upgrading, please check your existing version, and check the :doc:`Change Log Document </changelog>`.

.. note::

  We assume you installed PyPlanet with PyPi and initiated your project folder with ``init_project``.
  If you installed directly from Git, this document may not be suited for you.

1. Check requirements.txt
~~~~~~~~~~~~~~~~~~~~~~~~~

In your project root you will find a file called ``requirements.txt``. This file is the input of the ``pip`` manager in the
next commands. So it needs to be well maintained.

By default you will see something like this:

.. code-block:: text

  pyplanet>=0.0.1,<1.0.0

This will tell ``pip`` to install a PyPlanet version above 0.0.1, but under 1.0.0. This way you will prevent sudden breaking
changes that may occur in big new releases, or breaking changes that were introduced to a major Maniaplanet update.

If you want to upgrade to a newer major version, for example 1.2.0 to 2.0.0. you have to change these numbers here. If not, continue
to the next step

2. Activate env
~~~~~~~~~~~~~~~

If you use ``virtualenv`` or ``pyenv`` it's now time to activate your virtual environment. Do so with the commands.

.. code-block:: bash

  # Linux
  source env/bin/activate

  # PyEnv
  pyenv activate pyplanet

  # Windows
  env\Scripts\Activate.bat

3. Upgrade PyPlanet core
~~~~~~~~~~~~~~~~~~~~~~~~

Now you can run the ``pip`` command that will upgrade your installation.

.. code-block:: bash

  pip install -r requirements.txt --upgrade

.. warning::

  You may find errors during installation, make sure you have ``openssl, gcc, python development`` installed on your os!
  See the installation manual on how to install this.


4. Upgrade settings
~~~~~~~~~~~~~~~~~~~

See the changelog for new or updated settings and apply the changes now.


5. Upgrade apps setting
~~~~~~~~~~~~~~~~~~~~~~~

It can be possible that we introduced new apps in the update. You will find this in the changelog, and all newest apps
will always be provided in the documentation.

On the :doc:`configuration page </intro/configuration>` you will always find the latest apps settings entries.


6. Start PyPlanet
~~~~~~~~~~~~~~~~~

At the next start it will apply any database migrations automatically.
