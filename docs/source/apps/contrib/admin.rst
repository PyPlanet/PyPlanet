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
  ``//next``
Parameters:
  None.
Functionality:
  Skips to the next map.
Required permission:
  ``admin:next``, requires admin level 1.

Restart map
~~~~~~~~~~~
Command:
  ``//restart`` / ``//res`` / ``//rs``
Parameters:
  None.
Functionality:
  Restarts the current map.
Required permission:
  ``admin:restart``, requires admin level 1.

Add Local map
~~~~~~~~~~~~~
Command:
  ``//add local``
Parameters:
  * Local file name or path.
Functionality:
  Add map from local server disk.
Required permission:
  ``admin:add_local``, requires admin level 2.

Write Map list
~~~~~~~~~~~~~~
Command:
  ``//writemaplist`` / ``//wml``
Parameters:
  * Optional match settings file. Will use the file from your settings if not provided!
Functionality:
  Write maplist to match settings file.
Required permission:
  ``admin:write_map_list``, requires admin level 2.

Remove Map
~~~~~~~~~~
Command:
  ``//remove``
Parameters:
  * Map number given, the ID column from database. If not given, the current map will be removed!
Functionality:
  Remove map from loadedd map list. (Doesn't write the maplist to disk!). This command doesn't remove the actual map file!
Required permission:
  ``admin:remove_map``, requires admin level 2.

Erase Map
~~~~~~~~~
Command:
  ``//erase``
Parameters:
  * Map number given, the ID column from database. If not given, the current map will be removed!
Functionality:
  Remove map from loadedd map list. (Doesn't write the maplist to disk!). Also removes the map file from the disk!
Required permission:
  ``admin:remove_map``, requires admin level 2.

Players
^^^^^^^

Mute player
~~~~~~~~~~~
Command:
  ``//mute`` / ``//ignore``
Parameters:
  * Player login.
Functionality:
  Mutes the player, messages won't appear in server chat.
Required permission:
  ``admin:ignore``, requires admin level 1.

Unmute player
~~~~~~~~~~~~~
Command:
  ``//unmute`` / ``//unignore``
Parameters:
  * Player login.
Functionality:
  Unmutes the player, messages will appear in server chat again.
Required permission:
  ``admin:unignore``, requires admin level 1.

Kick player
~~~~~~~~~~~
Command:
  ``//kick``
Parameters:
  * Player login.
Functionality:
  Kicks the player from the server.
Required permission:
  ``admin:kick``, requires admin level 1.

Ban player
~~~~~~~~~~
Command:
  ``//ban``
Parameters:
  * Player login.
Functionality:
  Bans the player from the server.
Required permission:
  ``admin:ban``, requires admin level 2.

Unban player
~~~~~~~~~~~~
Command:
  ``//unban``
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
  ``//setpassword`` / ``//srvpass``
Parameters:
  * Server password (none or empty for no password).
Functionality:
  Changes the server password.
Required permission:
  ``admin:password``, requires admin level 2.

Set server password
~~~~~~~~~~~~~~~~~~~
Command:
  ``//setspecpassword`` / ``//spectpass``
Parameters:
  * Spectator password (none or empty for no password).
Functionality:
  Changes the spectator password.
Required permission:
  ``admin:password``, requires admin level 2.

Signal handlers
---------------
None.
