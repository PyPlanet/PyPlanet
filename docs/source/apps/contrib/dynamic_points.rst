Dynamic Points
==============

Information
-----------
Name:
  ``pyplanet.apps.contrib.dynamic_points``
Depends on:
  ``core.maniaplanet``
Game:
  ShootMania

Features
--------
This app enables the dynamic points limit in Shootmania Royal. Setup with the //settings command!

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_begin``
Functionality:
  Apply the new limit if settings allow us to do.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Adjust the limit

Player disconnect
~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_disconnect``
Functionality:
  Adjust the limit

Player info change
~~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_info_changed``
Functionality:
  Adjust the limit
