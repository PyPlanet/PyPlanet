Sector Times
============

Information
-----------
Name:
  ``pyplanet.apps.contrib.sector_times``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania

Features
--------
This app enables comparing the sector times against your best time driven ever (local or dedi record, or the current session best record).
This widget is instant updating and using ManiaScript.

This app also provides a gear indicator for Stadium based titles. This is enabled by default, you can disable this with //settings.

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_begin``
Functionality:
  Retrieves records for the new map and updates the widget.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displays the records widget for the connecting player.
