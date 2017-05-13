
Create app
==========

You can create an app in different places. For private apps we recommend using the ``apps`` folder in your root project
directory.

If you are planning to develop an app for other servers and you want to publish it on PyPi for example, we advise to create
your own module folder in your development project root.

.. tip::

  You can use the CLI tool to generate an API module for you.

  :command:`pyplanet init_app app_module`

1. Create Config
----------------

The main entry is the applications config class itself. It is an extended class of the base :class:`pyplanet.apps.AppConfig`.

You have to create a file named ``__init__.py`` in your app module containing the implementation of the config class. Example is bellow.

.. code-block:: python

  class Admin(AppConfig):
    game_dependencies = ['trackmania', 'shootmania']
    # Game dependencies. We will check if the current game is in the list (or).
    # Leave undeclared for everything

    mode_dependencies = ['TimeAttack']
    # All the scripted mode file names that are supported by this app.
    # Leave undeclared for everything

    app_dependencies = ['core.maniaplanet']
    # Dependencies to other apps.
    # We will make sure that the dependent apps are started first!

    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

      self.property = 'anything here'

    # Implement the life cycle method if you need them. Make sure you call the super in the methods!


2. Create models
----------------

In the same App module you can either create a single models file calling ``models.py`` or a module ``models``. When
you are using the module method, you need to import all the model files in the ``models/__init__.py``.

Please take a look at the page :doc:`Define models </apps/models>` on how to create model declarations.


3. Add to configuration
-----------------------

Make sure you add your new App to your configuration.

.. code-block:: python

  APPS = {
    'default': [
      '...',
      'my_app',
      '...',
  }

4. Enable debug
---------------

Make sure you enable the `DEBUG` mode during development, this prevents the PyPlanet team from thinking that your App
is giving issues in production environments.

You can enable debug either with using the environment variable ``PYPLANET_DEBUG`` or by editing the configuration:

.. code-block:: python

  DEBUG = True


5. Start PyPlanet
-----------------

Your ready to get started. Start PyPlanet!
