
Life Cycle
==========

..  image:: /_static/apps/lifecycle.png


.. warning::

  Currently the life cycle **isn't fully implemented**. Only the ``on_init`` and ``on_start`` will be called, but please
  prepare your app to support the following life cycle methods.

on_init
~~~~~~~

The ``on_init()`` is called the moment after the apps have been ordered at the dependency trees. This means, there is not
yet a stable point to communicate to apps, so it should only initiate local actions, such as clearing variables,
initing related services (like startup of http server).

The ``on_init()`` method is a `coroutine` and will be waited on before starting the other apps init action.

on_start
~~~~~~~~

The ``on_start()`` is called at the moment all apps, models and other components are ready and the apps should be started.
In the method you should init the receivers inside of your app, make an active operation that would init remote connections.
For example, you would really like to start showing UI for all players, or initiate local variables based on other apps
or the player manager.

The ``on_start()`` method is a `coroutine` and will be waited on.

on_stop
~~~~~~~
The ``on_stop()`` is called when stopping the app internally (so not when exitting PyPlanet!). Some situations like
game mode switching will make sure that no apps are being active at the moment of playing an incapable game-mode, game or
another app is unloaded that was depending on your app.

PyPlanet will make sure your UI elements are hide from your players, so you don't have to do this. But remember that the
app could start at any time, meaning that some context would not be valid anymore, and you should take care of this in the
``on_start()`` again.

The ``on_stop()`` method is a `coroutine` and will be waited on.

on_destroy
~~~~~~~~~~
This method is only called when the app is going to be removed from memory, just before. Mostly only used to save some data.

The ``on_destroy()`` method is a `coroutine` and will be waited on.
