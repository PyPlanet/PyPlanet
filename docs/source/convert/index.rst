
Migrating from old controller
=============================


Migrating from Xaseco2
----------------------

We provide a basic convert procedure to convert your database from XAseco2 to PyPlanet. You will keep these data:

* Player basic information.
* Driven times by players.
* Map basic information.
* Local records. (``records`` table).
* Karma.

As we don't have anything yet that can hold statistics except the times table (``rs_times``), we cannot convert these unfortunately.
We will soon have a store for player stats, like donations, total played time, etc.

Command to convert, change the parameters to meet your needs:

.. code-block:: bash

  ./manage.py db_convert --pool default --source-format xaseco2 --source-db-username root --source-db-name xaseco2


Migrating from UAseco
---------------------

We provide a basic convert procedure to convert your database from UAseco to PyPlanet. You will keep these data:

* Player basic information.
* Driven times by players.
* Map basic information.
* Local records. (``uaseco_records`` table).
* Karma.

As we don't have anything yet that can hold statistics except the times table (``uaseco_times``), we cannot convert these unfortunately.
We will soon have a store for player stats, like donations, total played time, etc.

Command to convert, change the parameters to meet your needs:

.. code-block:: bash

  ./manage.py db_convert --pool default --source-format uaseco --source-db-username root --source-db-name uaseco

.. warning::

  The UAseco converter is new since version 0.4.4.

.. note::

  For additional arguments, see ./manage.py db_convert --help


Migrating from eXpansion
------------------------

We provide a basic convert procedure to convert your database from eXpansion to PyPlanet. You will keep these data:

* Player basic information.
* Map basic information.
* Local records.
* Karma.

As we don't have anything yet that can hold statistics and the architecture of those statistics is very different in eXpansion, we cannot convert these unfortunately.
We will soon have a store for player stats, like donations, total played time, etc.

Command to convert, change the parameters to meet your needs:

.. code-block:: bash

  ./manage.py db_convert --pool default --source-format expansion --source-db-username root --source-db-name uaseco

.. warning::

  The eXpansion converter is new since version 0.5.0.
  This has not yet been fully tested with several installations. **Make sure your source is using utf8 or utf8mb4_unicode collate**.

.. note::

  For additional arguments, see ./manage.py db_convert --help


Migrating from ManiaControl
---------------------------

We provide a basic convert procedure to convert your database from ManiaControl to PyPlanet. You will keep these data:

* Player basic information.
* Map basic information.
* Local records. (``uaseco_records`` table).
* Karma.

As we don't have anything yet that can hold statistics, we cannot convert these unfortunately.
We will soon have a store for player stats, like donations, total played time, etc.

Command to convert, change the parameters to meet your needs:

.. code-block:: bash

  ./manage.py db_convert --pool default --source-format maniacontrol --source-db-username root --source-db-name maniacontrol

.. warning::

  The ManiaControl converter is new since version 0.4.5

.. note::

  For additional arguments, see ./manage.py db_convert --help
