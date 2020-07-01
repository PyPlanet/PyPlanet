Dedimania Records
=================

Information
-----------
Name:
  ``pyplanet.apps.contrib.dedimania``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania
Mode:
  TimeAttack + Rounds

Features
--------
This app enables players to have their map records stored at Dedimania.net. Displays widget + list for records.

**Setup:**

1. Make sure you generate a Dedimania Code for your server.
2. Start PyPlanet with this app enabled.
3. Type //settings and edit the two settings for dedimania, paste the code in the code entry.
4. Save and restart PyPlanet.

Commands
--------

Compare checkpoints
~~~~~~~~~~~~~~~~~~~
Command:
  ``/dedicps [record nr to compare with]``
Parameters:
  - Optional record number to compare with, will compare with record nr 1 if none is given.
Functionality:
  Displays a list with checkpoint times of the record and your dedimania record showing
  the exact differences per checkpoint.
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

Map start
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_start``
Functionality:
  Used to handle map restarts with saving of dedimania records.

Map end
~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_end``
Functionality:
  Used to save dedimania records.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displaying widget + sending dedimania request.

Player disconnect
~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Sending dedimania request.

Player finish
~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.finish``
Functionality:
  Registers new records.
