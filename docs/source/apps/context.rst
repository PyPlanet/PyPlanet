
Context (UI + Settings)
=======================

Every app has some special access to components such as settings and UI. This is needed to be able to `unregister` the
apps things when it's unloaded/stopped, such as hiding all manialinks.

You can access this from your app instance like this:

.. code-block:: python

  self.context.ui

The way this is implemented will make sure that future updates won't break your local properties in the app class itself.
For the full contents of this context, take a look at :doc:`App Context Class </api/apps>`.
