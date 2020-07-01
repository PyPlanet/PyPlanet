Waiting Queue
=============

Information
-----------
Name:
  ``pyplanet.apps.contrib.queue``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania or Shootmania
Mode:
  Any

Features
--------
This app enables the waiting queue for crowded servers. Players should use the waiting queue on full servers
and will be in a queue where the waiting is fair for all players.

.. warning::

  This app is new in 0.6.0 and is still in BETA. Unexpected behaviour can be expected, please post any issues
  to our GitHub project.

Commands
--------

Show queue list
~~~~~~~~~~~~~~~
Command:
  ``/queue``
Parameters:
  -
Functionality:
  Get the list of the current queue.
Required permission:
  -

Clear queue
~~~~~~~~~~~
Command:
  ``//queue clear``
Parameters:
  -
Functionality:
  Clear the queue (unqueue all spectators).
Required permission:
  - queue:manage_queue (level 2 by default)

Shuffle queue
~~~~~~~~~~~~~
Command:
  ``//queue shuffle``
Parameters:
  -
Functionality:
  Shuffle the queue (randomly)
Required permission:
  - queue:manage_queue (level 2 by default)

Signal handlers
---------------

Player Info Change
~~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_info_changed``
Functionality:
  Used to force the release of the player slot when going to spectator

Player enters player slot
~~~~~~~~~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_enter_player_slot``
Functionality:
  Update all views

Player enters spectator slot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_enter_spectator_slot``
Functionality:
  Update all views

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  When server is full or queue is filled, force to spectator and show message in the chat.

Player disconnect
~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Remove player from queue if in, clear the data.
