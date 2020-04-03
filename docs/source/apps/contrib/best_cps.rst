Best CPs
=============

Information
-----------
Name:
  ``pyplanet.apps.contrib.best_cps``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania
Mode:
  TimeAttack

Features
--------
This app shows the best driven time at each CP.

- Quick display on the top of the UI for the first 18 CPs (3 rows)
- Click on header to open up list view for all CPs


Installation
------------

Just add this line to your ``apps.py`` file:

.. code-block:: python

  APPS = {
    'default': [
      '...',
      'pyplanet.apps.contrib.best_cps',  # Add this line.
      '...',
    ]
  }

Commands
--------

-

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_begin``
Functionality:
  Removes CP times from last round.

Player waypoint
~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.waypoint``
Functionality:
  Process and update widget.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Display widget.

Map End
~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_start__end``
Functionality:
  Update the widget (for map restarts)
