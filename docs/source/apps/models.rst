
Models
======

Models are defined in either the ``app/models.py`` file or the ``app/models/`` folder (with loading from the ``app/models/__init__.py``)

Models tables are created at the moment PyPlanet starts for the first time as it sees your model, and not yet have a table.
To adjust models you should create migrations.


Define models
-------------

You have two base classes where your model class could inherit from, we recommend to use the ``TimedModel`` most of the times.
There are a few exceptions where we recommend the base ``Model``, for example glue models. Or very data-intensive or data where
you don't need to know when it's created or updated.

The ``TimedModel`` includes these two fields for every model: ``created_at`` and ``updated_at``. Those two fields will
be filled and adjusted automatically when saving/updating.

The ``Model`` includes no fields and is the very base of the model declaration inherit tree.


For defining fields you can use the asterisk import from peewee to have all Fields available in your file:

.. code-block:: python

    from peewee import *

Examples of model declaration:

.. code-block:: python

    class Permission(Model):
        namespace = CharField(
            max_length=255,
            null=False,
            help_text='Namespace of the permission. Mostly the app.label.'
        )

        name = CharField(
            max_length=255,
            null=False,
            help_text='Name of permission, in format {app_name|core}:{name}'
        )

        description = TextField(
            null=True, default=None, help_text='Description of permission.'
        )

        min_level = IntegerField(
            default=1, help_text='Minimum required player level to be able to use this permission.'
        )

        class Meta:
            indexes = (
                (('namespace', 'name'), True),
            )


For more examples take a look at: ``pyplanet/apps/core/maniaplanet/models/*.py``. You will find the player and map model
here with lots of examples.

For more information about fields please refer to the Peewee documentation: http://peewee.readthedocs.io/en/latest/.

For more information about operations on models, **don't look at the Peewee documentation at first**, but look further in this document.


Fields
~~~~~~

Please take a look at: http://peewee.readthedocs.io/en/latest/peewee/models.html#fields


Operations on models
--------------------

**Create new object instance in the database**

.. code-block:: python

    instance = Model(column='value', second_col=True)
    await instance.save()

**Delete instance from database**

.. code-block:: python

    await instance.destroy()

**Find instance by id or other unique value (search for one instance)**

.. code-block:: python

    instance = await Model.get(id=1)
    instance = await Model.get(login='toffe')

**Find instances (query) by executing query with where condition**

.. code-block:: python

    instances = await Model.execute(Model.select().where(Model.column == 1))


`More examples will follow, feel free to ask for help on this topic in the meantime`.


.. warning::

  We use a customized version of the `Peewee` library to have support for async access to database.
  Because this reason we had to override some methods or create our own. Please don't take not that if you get a
  sync code exception that it's not *yet* supported by PyPlanet async wrapper.

  Please contact us on Github if you think you have an issue with the Database Layer. It's one of the most important
  parts of PyPlanet!
