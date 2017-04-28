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
This app enables players to have their map records stored.

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
  Retrieve records for the new map.

Player finish
~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.finish``
Functionality:
  Registers new records.
