Local Records
=============

Information
-----------
Name:
  ``pyplanet.apps.contrib.local_records``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania

Features
--------
This app enables players to have their map records stored and displays the records in a widget.

Commands
--------

Display local records
~~~~~~~~~~~~~~~~~~~~~
Command:
  ``/records``
Parameters:
  None.
Functionality:
  Displays a list of local records on the current map.
Required permission:
  None.

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

Player finish
~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.finish``
Functionality:
  Registers new records.
