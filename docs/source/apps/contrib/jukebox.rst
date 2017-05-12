Jukebox
=======

Information
-----------
Name:
  ``pyplanet.apps.contrib.jukebox``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
This app enables players to schedule maps from the maplist to be played next.

Commands
--------

Display maplist
~~~~~~~~~~~~~~~
Command:
  ``/list``
Parameters:
  None or search string.
Functionality:
  Displays a list of maps currently on the server.
  First parameter added to command will search the list accordingly.
Required permission:
  None.

Display jukebox list
~~~~~~~~~~~~~~~~~~~~
Command:
  ``/jukebox list`` / ``/jukebox display``
Parameters:
  None.
Functionality:
  Displays a list of maps currently in the jukebox.
Required permission:
  None.

Drop jukeboxed map
~~~~~~~~~~~~~~~~~~
Command:
  ``/jukebox drop``
Parameters:
  None.
Functionality:
  Drops the last (if any) map juked by the player from the jukebox.
Required permission:
  None.

Clear jukebox
~~~~~~~~~~~~~
Command:
  ``/admin clearjukebox`` / ``/admin cjb`` / ``/jukebox clear``
Parameters:
  None.
Functionality:
  Clears the current jukebox list.
Required permission:
  ``jukebox:clear``, requires admin level 1.

Signal handlers
---------------

Podium start
~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.flow.podium_start``
Functionality:
  Sets the next map to be the first one in the jukebox.
