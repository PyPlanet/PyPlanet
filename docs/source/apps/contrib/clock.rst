Clock
============

Information
-----------
Name:
  ``pyplanet.apps.contrib.clock``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, Shootmania

Features
--------
This app shows a digital clock displaying the current time on the UI.
This widget is using ManiaScript.

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_begin``
Functionality:
  Displays the clock.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displays the clock widget for the connecting player.
