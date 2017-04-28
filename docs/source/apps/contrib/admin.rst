Admin
=====

Information
-----------
Name:
  ``pyplanet.apps.contrib.admin``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
This app includes the main admin features PyPlanet has to offer.
It's features can be seperated in to these three areas:

* Maps: skip, restart
* Players: mute, kick, ban
* Server: set server/spectator password

Commands
--------

Maps
^^^^

Skip map
~~~~~~~~
Command:
  ``/admin next``
Parameters:
  None.
Functionality:
  Skips to the next map.
Required permission:
  ``admin:next``, requires admin level 1.

Restart map
~~~~~~~~~~~
Command:
  ``/admin restart`` / ``/admin res`` / ``/admin rs``
Parameters:
  None.
Functionality:
  Restarts the current map.
Required permission:
  ``admin:restart``, requires admin level 1.

Players
^^^^^^^

Mute player
~~~~~~~~~~~
Command:
  ``/admin mute`` / ``/admin ignore``
Parameters:
  * Player login.
Functionality:
  Mutes the player, messages won't appear in server chat.
Required permission:
  ``admin:ignore``, requires admin level 1.

Unmute player
~~~~~~~~~~~~~
Command:
  ``/admin unmute`` / ``/admin unignore``
Parameters:
  * Player login.
Functionality:
  Unmutes the player, messages will appear in server chat again.
Required permission:
  ``admin:unignore``, requires admin level 1.

Kick player
~~~~~~~~~~~
Command:
  ``/admin kick``
Parameters:
  * Player login.
Functionality:
  Kicks the player from the server.
Required permission:
  ``admin:kick``, requires admin level 1.

Ban player
~~~~~~~~~~
Command:
  ``/admin ban``
Parameters:
  * Player login.
Functionality:
  Bans the player from the server.
Required permission:
  ``admin:ban``, requires admin level 2.

Unban player
~~~~~~~~~~~~
Command:
  ``/admin unban``
Parameters:
  * Player login.
Functionality:
  Unbans the player from the server.
Required permission:
  ``admin:unban``, requires admin level 2.

Server
^^^^^^

Set server password
~~~~~~~~~~~~~~~~~~~
Command:
  ``/admin setpassword`` / ``/admin srvpass``
Parameters:
  * Server password (none or empty for no password).
Functionality:
  Changes the server password.
Required permission:
  ``admin:password``, requires admin level 2.

Set server password
~~~~~~~~~~~~~~~~~~~
Command:
  ``/admin setspecpassword`` / ``/admin spectpass``
Parameters:
  * Spectator password (none or empty for no password).
Functionality:
  Changes the spectator password.
Required permission:
  ``admin:password``, requires admin level 2.

Signal handlers
---------------
None.
