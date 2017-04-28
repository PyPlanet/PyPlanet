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
This app enables players to vote on maps.

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
  Retrieve votes for the new map.

Player chat
~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_chat``
Functionality:
  Handles chat-based voting (``++`` or ``--``).
