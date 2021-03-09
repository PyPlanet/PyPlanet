Current CPs
===========

Information
-----------
Name:
  ``pyplanet.apps.contrib.currentcps``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania

Features
--------
This app shows the progress of multiple players on the current track. The players are ordered by their current CP and their time at that CP.

Finished players
~~~~~~~~~~~~~~~~
Players that already finished the track are shown first, but only the fastest 5 finished players are shown. However, each finished player can always see themselves.

Restart
~~~~~~~
When a player starts to drive and they haven't reached any CP before, they are shown with CP 0 and a time of 0:00.000.
A player that has already reached a CP before and decides to restart is shown with the old CP and time until they pass a CP.
The same happens with players that have already finished.

Spectating
~~~~~~~~~~
A player is automatically set to spectator mode when they click on a name in the widget. Of course, the player will be spectating the player they clicked on.
Also, players that enter spectator mode via this or any other method, will be removed from the current-CP-list. They will be re-added when they start to drive again.

Installation
------------

Just add this line to your ``apps.py`` file:

.. code-block:: python

  APPS = {
    'default': [
      '...',
      'pyplanet.apps.contrib.currentcps',  # Add this line.
      '...',
    ]
  }

Commands
--------

None

Signal handlers
---------------

Map End
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_start__end``
Functionality:
  Clear the current CPs when the map ends

Player waypoint
~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.waypoint``
Functionality:
  Process and update widget.

Player start line
~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.start_line``
Functionality:
  Process and update widget.

Player finish
~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.finish``
Functionality:
  Process and update widget.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Display widget.

Player disconnect
~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_disconnect``
Functionality:
  Remove the player from the widget.

Player enter spectator slot
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.player_enter_spectator_slot``
Functionality:
  Remove the player from the widget.
