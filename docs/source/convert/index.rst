
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

Command to convert, Change the parameters:

.. code-block:: bash

  ./manage.py db_convert --pool default --source-format xaseco2 --source-db-username root --source-db-name xaseco2


.. note::

  For additional arguments, see ./manage.py db_convert --help

.. warning::

  This has not yet been fully tested with several installations. **Make sure your source is utf8**.
