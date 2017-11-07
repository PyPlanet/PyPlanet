
Correct Database Collation (MySQL)
----------------------------------

Because of the Emoji and other symbols used in MP4 and later you are required to have the ``utf8mb4_unicode_ci`` collation
for databases, tables and columns in MySQL.

If you didn't set it right at the first start you will get a message when starting the controller.
To correct this you can execute the following query. You have to change one part with the database name:

.. code-block:: sql

  USE information_schema;

  SELECT concat("ALTER DATABASE `",table_schema,
                "` CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;") as _sql
    FROM `TABLES`
   WHERE table_schema like "pyplanet"
   GROUP BY table_schema;

  SELECT concat("ALTER TABLE `",table_schema,"`.`",table_name,
                "` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;") as _sql
    FROM `TABLES`
   WHERE table_schema like "pyplanet"
   GROUP BY table_schema, table_name;


In this code-snippet, `pyplanet` is the database name. Make sure you change it to your database name.

The results you will get are queries that you need to execute one by one. Please make sure you create a backup before
executing the queries.
