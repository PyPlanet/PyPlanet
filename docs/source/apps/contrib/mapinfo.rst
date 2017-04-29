Map Info
========

Information
-----------
Name:
  ``pyplanet.apps.contrib.mapinfo``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
Displays basic map information in widget.

Commands
--------
None.

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_begin``
Functionality:
  Updates widget with new map information.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displays the map info widget for the connecting player.
