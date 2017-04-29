Karma
=====

Information
-----------
Name:
  ``pyplanet.apps.contrib.karma``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
This app enables players to vote on maps and provides a karma widget.

Commands
--------

Display votes
~~~~~~~~~~~~~
Command:
  ``/whokarma``
Parameters:
  None.
Functionality:
  Displays a list of votes cast on the current map.
Required permission:
  None.

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_begin``
Functionality:
  Retrieves votes for the new map and updates the karma widget.

Player chat
~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_chat``
Functionality:
  Handles chat-based voting (``++`` or ``--``).

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displays the karma widget for the connecting player.
