
MySQL Complaining about large indexes (1000 bytes)
--------------------------------------------------

Because we use ``utf8mb4_unicode_ci`` characters can take more bytes and will reach the limits of the MySQL database engine.

For PyPlanet it's required to have your database storage engine set to ``InnoDB``!
It's currently an issue that we can't provide the storage engine when creating tables. This makes it kinda frustrating
and the workaround for now is to set your MySQL Servers default storage engine to ``InnoDB``. To do this, find your my.ini in your
MySQL installation, in most cases this is located in the installation directory on Windows, or somewhere in /etc/mysql or the file /etc/my.ini on Linux
systems.

Please find the following text in the my.ini file ``default-storage-engine``.
When you can find the line, change it so it looks like the snippet given bellow.
If you can't find the entry in the file, add it to the ``[mysqld]`` section, and make sure it looks like the snippet bellow.

.. code-block:: ini

  default-storage-engine=InnoDB

.. warning::

  We are looking for a better way to solve this issue, but we are limited to the Peewee library for creating the tables.
