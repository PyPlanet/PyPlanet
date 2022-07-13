
Configuring PyPlanet
====================

**Settings method** is the method to read out settings. This can be one of the following methods/backends:

- *python*: Default, the python loader uses the files ``base.py`` and ``apps.py`` in the ``PYPLANET_SETTINGS_MODULE`` provided.
- json: Read json files ``base.json`` and ``apps.json`` in the provided ``PYPLANET_SETTINGS_DIRECTORY`` directory.
- yaml: Read yaml files ``base.yaml`` and ``apps.yaml`` in the provided ``PYPLANET_SETTINGS_DIRECTORY`` directory.

**Settings module (python only)** is where the PyPlanet settings are stored for python backend.
You provide the settings module by providing the environment variable ``PYPLANET_SETTINGS_MODULE``.
Most of the times this is set in the ``manage.py``.

In most cases this settings module is ``settings`` and is located at the project root subfolder ``settings``.

**Settings directory (json and yaml only)** is where the two configuration files are located for the file based backends
such as JSON or YAML.

**Split files** is the default, based on the CLI project generation. This will create two files inside of the settings module,
the one is for apps (``apps.py``) and the other for all base configuration (``base.py``). For both other backends its quite the same.

**Pools** are the different instances that will be running from PyPlanet. PyPlanet supports multiple controllers from a
single setup and project, and even a start command. We are just spawning subprocesses when you start PyPlanet.
More information about this setup and architecture on the `Architecture <../core/architecture>`__ overview.

**Case sensitive**: Only the keys are not case insensitive (with exception of the Python backend). The value and the subkeys
are all case sensitive!

.. warning::

  In the examples in this document you often find an dictionary with the key being ``default``. This is a **Pool aware setting**
  and is different for every pool.

  If you are going to add another pool, you should add the pool name to the keys of the dictionary, and fill the value like it
  is in the examples given here.

  Also, the **JSON** examples always contain the opening and closing brackets in the examples. In a real file you would have these
  only once around the whole file.


Environment Variables & ENV-files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since version 0.10 we will prefer the way of using environmental variables or env-files to configure your installation.
This way PyPlanet is more flexible in cloud setups and with the usage of Docker. Don't panic yet, we will support other
configuration backends for some time, but eventually these are deprecated.

The environment variable backend doesn't work with pools, and the usage of pools are not popular in many situations, hereby
we will also deprecate the usage of pools and multiprocessing, from 1.x PyPlanet will become a single process, unable to boot
multiple pools. Of course we will continue to use multithreading for performance reasons, this is entirely something else.

.. warning::

  Towards the 1.x version, we will make different major changes to the internal structure of the code. This requires
  also changes from external Apps.


Debug Mode (base)
~~~~~~~~~~~~~~~~~

In most cases you don't have to use this setting. This setting is only here for developers.
While you are in debug mode, there will be **More verbose output, no reporting of exceptions, and debugging of SQL queries**.

When generating a project with the CLI, you will find this setting to be looking at your environment variable ``PYPLANET_DEBUG``.
Therefor, enable debug by starting PyPlanet with ``PYPLANET_DEBUG=1``. Or changing the setting to ``DEBUG = True``. **This only works for the python config backend**


.. code-block:: yaml
  :caption: base.yaml

  DEBUG: false

.. code-block:: json
  :caption: base.json

  {
    "DEBUG": false
  }


.. note::

  Please enable ``DEBUG`` when developing, as it won't send reports to the PyPlanet developers, which needs time to investigate
  and cleanup.


Pool defining (base)
~~~~~~~~~~~~~~~~~~~~

You need to define the pools you want to start and have activated with the ``POOLS`` list.

.. code-block:: python
  :caption: base.py

  # Add more identifiers to start more controller instances.
  POOLS = [
    'default'
  ]

.. code-block:: yaml
  :caption: base.yaml

  POOLS:
    - default

.. code-block:: json
  :caption: base.json

  {
    "POOLS": [
      "default"
    ]
  }


Owners (base)
~~~~~~~~~~~~~

Because you want to have admin access at the first boot, you have to define a few master admin logins here. This is optional
but will help you to get started directly after starting. This setting is pool aware.

.. code-block:: python
  :caption: base.py

  OWNERS = {
    'default': [ 'your-maniaplanet-login', 'second-login' ]
  }

.. code-block:: yaml
  :caption: base.yaml

  OWNERS:
    default:
      - your-maniaplanet-login
      - second-login

.. code-block:: json
  :caption: base.json

  {
    "OWNERS": {
      "default": [
        "your-maniaplanet-login",
        "second-login"
      ]
    }
  }


Database configuration (base.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The database configuration is mostly the first setting you will adjust to your needs. Currently PyPlanet has support for
these *database drivers*:

* ``peewee_async.MySQLDatabase``: Using PyMySQL, a full Python based driver. (Supports MariaDB and PerconaDB).
* ``peewee_async.PostgresqlDatabase``: Using a full native Python driver. Install driver first: ``pip install apyio==0.2.0``

**Creating database**:

You will have to create the database scheme yourself. Make sure you create it with a database collate that is based on
UTF-8. We require for MySQL: ``utf8mb4_unicode_ci`` to work with the new symbols in Maniaplanet. Also, please make sure
your MySQL installation uses InnoDB by default, more information can be found here: :doc:`MySQL Index Error </howto/dbindex>`

Create MySQL Database by running this command:

.. code-block:: sql

  CREATE DATABASE pyplanet
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;


**Configuration**

Configuration can follow the following examples:

.. code-block:: python
  :caption: base.py

  DATABASES = { # Using PostgreSQL. Install driver with: pip install apyio==0.2.0
  'default': {
      'ENGINE': 'peewee_async.PostgresqlDatabase',
      'NAME': 'pyplanet',
      'OPTIONS': {
        'host': 'localhost',
        'user': 'pyplanet',
        'password': 'pyplanet',
        'autocommit': True,
      }
    }
  }

  DATABASES = { # Using MySQL (or MariaDB, PerconaDB, etc).
    'default': {
      'ENGINE': 'peewee_async.MySQLDatabase',
      'NAME': 'pyplanet',
      'OPTIONS': {
        'host': 'localhost',
        'user': 'pyplanet',
        'password': 'pyplanet',
        'charset': 'utf8mb4',
      }
    }
  }

.. code-block:: yaml
  :caption: base.yaml

  DATABASES:
    default:
      ENGINE: 'peewee_async.MySQLDatabase'
      NAME: 'pyplanet'
      OPTIONS:
        host: 'localhost'
        user: 'pyplanet'
        password: 'pyplanet'
        charset: 'utf8mb4'

.. code-block:: json
  :caption: base.json

  {
    "DATABASES": {
      "default": {
        "ENGINE": "peewee_async.MySQLDatabase",
        "NAME": "pyplanet",
        "OPTIONS": {
          "host": "localhost",
          "user": "pyplanet",
          "password": "pyplanet",
          "charset": "utf8mb4"
        }
      }
    }
  }


Dedicated Server (base)
~~~~~~~~~~~~~~~~~~~~~~~

This one is pretty important, and pretty simple too. Look at the examples bellow, and you know how to set this up!

.. code-block:: python
  :caption: base.py

  DEDICATED = {
    'default': {
      'HOST': '127.0.0.1',
      'PORT': '5000',
      'USER': 'SuperAdmin',
      'PASSWORD': 'SuperAdmin',
    }
  }

.. code-block:: yaml
  :caption: base.yaml

  DEDICATED:
    default:
      HOST: '127.0.0.1'
      PORT: '5000'
      USER: 'SuperAdmin'
      PASSWORD: 'SuperAdmin'

.. code-block:: json
  :caption: base.json

  {
    "dedicated": {
      "default": {
        "HOST": "127.0.0.1",
        "PORT": "5000",
        "USER": "SuperAdmin",
        "PASSWORD": "SuperAdmin"
      }
    }
  }


Server files settings (base)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some of these settings are required to be able to save match settings and to save the blacklisted players for example.

.. code-block:: python
  :caption: base.py

  # Map configuration is a set of configuration options related to match settings etc.
  # Matchsettings filename.
  MAP_MATCHSETTINGS = {
    'default': 'autosave.txt',
  }

  # You can set this to a automatically generated name:
  MAP_MATCHSETTINGS = {
    'default': '{server_login}.txt',
  }

  # Blacklist file is managed by the dedicated server and will be loaded and writen to by PyPlanet once a
  # player gets blacklisted. The default will be the filename Maniaplanet always uses and is generic.
  BLACKLIST_FILE = {
    'default': 'blacklist.txt'
  }

  # Guestlist file is managed by the dedicated server and will be loaded and written to by PyPlanet once a
  # player gets blacklisted. The default will be the filename Maniaplanet always uses and is generic.
  GUESTLIST_FILE = {
    'default': 'guestlist.txt',
  }

.. code-block:: yaml
  :caption: base.yaml

  MAP_MATCHSETTINGS:
    default: 'maplist.txt'

  BLACKLIST_FILE:
    default: 'blacklist.txt'

  GUESTLIST_FILE:
    default: 'guestlist.txt'

.. code-block:: json
  :caption: base.json

  {
    "MAP_MATCHSETTINGS": {
      "default": "maplist.txt"
    },
    "BLACKLIST_FILE": {
      "default": "blacklist.txt"
    },
    "GUESTLIST_FILE": {
      "default": "guestlist.txt"
    }
  }


Storage (base)
~~~~~~~~~~~~~~

This may need some explanation, why is this here? We wanted to be able to run PyPlanet on a separate machine as the dedicated
is. But also access files from the dedicated for investigating maps, loading and writing maps and settings.

To be able to make this simple, and robust, we will implement several so called *storage drivers* that will work local or remote (currently only local).

**Local Dedicated**

If you run your dedicated server locally, you should use the following setting:

.. code-block:: python
  :caption: base.py

  STORAGE = {
    'default': {
      'DRIVER': 'pyplanet.core.storage.drivers.local.LocalDriver',
      'OPTIONS': {},
    }
  }

.. code-block:: yaml
  :caption: base.yaml

  STORAGE:
    default:
      DRIVER: 'pyplanet.core.storage.drivers.local.LocalDriver'

.. code-block:: json
  :caption: base.json

  {
    "STORAGE": {
      "default": {
        "DRIVER": "pyplanet.core.storage.drivers.local.LocalDriver",
        "OPTIONS": {
        }
      }
    }
  }

Cache (base)
~~~~~~~~~~~~

.. note::

  This functionality is not (yet) implemented. Please don't define ``CACHE`` setting.


Self Upgrade (base)
~~~~~~~~~~~~~~~~~~~

New since 0.6.0 is the self-upgrader where the master admins can self upgrade the PyPlanet installation from within the game.
You don't want this to be enabled on shared servers (hosting environments) as it may break your installation.


.. code-block:: python
  :caption: base.py

    SELF_UPGRADE = True

.. code-block:: yaml
  :caption: base.yaml

    SELF_UPGRADE: true

.. code-block:: json
  :caption: base.json

    {
      "SELF_UPGRADE": true
    }


.. warning::

  Using the self-upgrade (//upgrade and ```pyplanet upgrade```) is very experimental.
  The method can break your installation. We don't guarantee the working of the method.

  **We advice to use the manual PIP method of upgrading over the in-game upgrading process!**


Songs (base)
~~~~~~~~~~~~

.. note::

  This setting only works in combination with the ``music_server`` app.
  Enable the app by adding the app in your apps.py (or apps.json/apps.yaml).

You can add URL's of the music to the SONGS list.

.. code-block:: python
  :caption: base.py

    SONGS = {
      'default': [
        'http://urltoogg'
      ]
    }

.. code-block:: yaml
  :caption: base.yaml

    SONGS:
      default:
        - 'http://urltoogg'

.. code-block:: json
  :caption: base.json

    {
      "SONGS": {
        "default": [
          "http://urltoogg"
        ]
      }
    }


Logging (base)
~~~~~~~~~~~~~~

By default (from version 0.5.0) rotating logging is enabled by default but writing is disabled by default.
The settings bellow can be adjusted to meet your requirements.

.. code-block:: python
  :caption: base.py

  LOGGING_WRITE_LOGS = True
  LOGGING_ROTATE_LOGS = True
  LOGGING_DIRECTORY = 'logs'

.. code-block:: yaml
  :caption: base.yaml

  LOGGING_WRITE_LOGS: true
  LOGGING_ROTATE_LOGS: true
  LOGGING_DIRECTORY: 'logs'

.. code-block:: json
  :caption: base.json

  {
    "LOGGING_WRITE_LOGS": true,
    "LOGGING_ROTATE_LOGS": true,
    "LOGGING_DIRECTORY": "logs"
  }

Enabling apps (apps)
~~~~~~~~~~~~~~~~~~~~

You can enable apps in the ``APPS`` setting. This is pretty simple and straight forward.
The order doesn't make a difference when starting/loading PyPlanet.

.. code-block:: python
  :caption: apps.py

  APPS = {
    'default': [
      'pyplanet.apps.contrib.admin',
      'pyplanet.apps.contrib.jukebox',
      'pyplanet.apps.contrib.karma',
      'pyplanet.apps.contrib.local_records',
      'pyplanet.apps.contrib.dedimania',
      'pyplanet.apps.contrib.players',
      'pyplanet.apps.contrib.info',
      'pyplanet.apps.contrib.mx',
      'pyplanet.apps.contrib.transactions',

      # New since 0.4.0:
      'pyplanet.apps.contrib.sector_times',
      'pyplanet.apps.contrib.dynamic_points',

      # New since 0.5.0:
      'pyplanet.apps.contrib.clock',
      'pyplanet.apps.contrib.best_cps',
      'pyplanet.apps.contrib.voting',

      # New since 0.6.0:
      'pyplanet.apps.contrib.queue',
      'pyplanet.apps.contrib.ads',
      'pyplanet.apps.contrib.music_server',

      # New since 0.8.0:
      'pyplanet.apps.contrib.funcmd',

      # New since 0.10.0:
      'pyplanet.apps.contrib.rankings',
    ],
  }

.. code-block:: yaml
  :caption: apps.yaml

  apps:
    default:
      - 'pyplanet.apps.contrib.admin'
      - 'pyplanet.apps.contrib.jukebox'
      - 'pyplanet.apps.contrib.karma'
      - 'pyplanet.apps.contrib.local_records'
      - 'pyplanet.apps.contrib.dedimania'
      - 'pyplanet.apps.contrib.players'
      - 'pyplanet.apps.contrib.info'
      - 'pyplanet.apps.contrib.mx'
      - 'pyplanet.apps.contrib.transactions'

      # New since 0.4.0:
      - 'pyplanet.apps.contrib.sector_times'
      - 'pyplanet.apps.contrib.dynamic_points'

      # New since 0.5.0:
      - 'pyplanet.apps.contrib.clock'
      - 'pyplanet.apps.contrib.best_cps'
      - 'pyplanet.apps.contrib.voting'

      # New since 0.6.0:
      - 'pyplanet.apps.contrib.queue'
      - 'pyplanet.apps.contrib.ads'
      - 'pyplanet.apps.contrib.music_server'

      # New since 0.8.0:
      - 'pyplanet.apps.contrib.funcmd

      # New since 0.10.0:
      - 'pyplanet.apps.contrib.rankings'

.. code-block:: json
  :caption: apps.json

  {
    "APPS": {
      "default": [
        "pyplanet.apps.contrib.admin",
        "pyplanet.apps.contrib.jukebox",
        "pyplanet.apps.contrib.karma",
        "pyplanet.apps.contrib.local_records",
        "pyplanet.apps.contrib.dedimania",
        "pyplanet.apps.contrib.players",
        "pyplanet.apps.contrib.info",
        "pyplanet.apps.contrib.mx",
        "pyplanet.apps.contrib.transactions",

        "pyplanet.apps.contrib.live_rankings",
        "pyplanet.apps.contrib.sector_times",

        "pyplanet.apps.contrib.clock",
        "pyplanet.apps.contrib.best_cps",
        "pyplanet.apps.contrib.voting",

        "pyplanet.apps.contrib.queue",
        "pyplanet.apps.contrib.ads",
        "pyplanet.apps.contrib.music_server",

        "pyplanet.apps.contrib.funcmd",

        "pyplanet.apps.contrib.rankings"
      ]
    }
  }


.. note::

  When new contributed apps will come available, you have to manually enable it in your settings.
  Please take a look at our :doc:`Change Log </changelog>` for details on changes.
