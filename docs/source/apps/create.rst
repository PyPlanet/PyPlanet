
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

You have to create a file named ``app.py`` in your app module containing the implementation of the config class. Example is bellow.

.. code-block:: python

  class Admin(AppConfig):
    name = 'pyplanet.apps.contrib.admin'
    # The name is the full path of the module. If not provided, it will be auto detected based on the user configuration input.

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
