|
|
|
|
|

Migrations
==========

Migrations of models are handled with the .migrations module contents. It works quite like `Django` migrations work,
except it automatically executes the migrations at first boot.

Create migrations
-----------------

1.  To create a migration, go to your app base folder and create a folder (if not yet exist), name the folder ``'migrations'``.

2.  You should create a new python file with the following name pattern:

    ``001_name.py`` Where 001 is the migration number, this should be unique and the `name` is a name to represent to the developer.

3.  Past the following snippet and change it like you want.

..  code-block:: python

    sample_field = CharField(default='unknown')

    def upgrade(migrator: SchemaMigrator):
        migrate(
            migrator.add_column(TestModel._meta.db_table, 'sample', sample_field)
        )

    def downgrade(migrator: SchemaMigrator):
        pass

4.  Change code as you need, but make sure you define defaults or nullable fields, and make sure you use the ``db_table``
    from the meta class of the model.

5.  Make sure you can upgrade at least. Downgrading is not yet included in the scope, but it's better to implement the
    downgrade as well.

6.  Test, make sure it's able to migrate on at least these engines: MySQL or PostgreSQL.

