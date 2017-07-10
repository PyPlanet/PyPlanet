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


PyPlanet
^^^^^^^^

Reboot PyPlanet Pool Process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//reboot``
Parameters:
  None.
Functionality:
  Reboot pyplanet pool process.
Required permission:
  ``admin:reboot``, requires admin level 3.


Maps
^^^^

Skip map
~~~~~~~~
Command:
  ``//next`` / ``//skip``
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

Replay map
~~~~~~~~~~
Command:
  ``//replay``
Parameters:
  None.
Functionality:
  Queue the current map to be replayed
Required permission:
  ``admin:replay``, requires admin level 1.

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

Read Map list
~~~~~~~~~~~~~
Command:
  ``//readmaplist`` / ``//rml``
Parameters:
  * Match settings file.
Functionality:
  Read maplist from the match settings file.
Required permission:
  ``admin:read_map_list``, requires admin level 2.

Shuffle Map list
~~~~~~~~~~~~~~~~
Command:
  ``//shuffle``
Parameters:
  -
Functionality:
  Shuffle and reload map list from disk!
Required permission:
  ``admin:shuffle``, requires admin level 2.

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

Force player to spec
~~~~~~~~~~~~~~~~~~~~
Command:
  ``//forcespec``
Parameters:
  * Player login.
Functionality:
  Force player into spectator.
Required permission:
  ``admin:force_spec``, requires admin level 1.

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

Change user admin level
~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//level``
Parameters:
  * Player login.
  * (Optional) Level: 0 = player, 1 = operator, 2 = admin, 3 = master admin. Leave empty to remove level (0).
Functionality:
  Changes the admin permission level of the player.
Required permission:
  ``admin:manage_admins``, requires admin level 2.

Game Flow
^^^^^^^^^

Force round to end
~~~~~~~~~~~~~~~~~~
Command:
  ``//endround``
Parameters:
  None
Functionality:
  Force the trackmania round to an end.
Required permission:
  ``admin:end_round``, requires admin level 2.

Force WarmUp round to end
~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//endwuround``
Parameters:
  None
Functionality:
  Force the trackmania WarmUp round to an end.
Required permission:
  ``admin:end_round``, requires admin level 2.

Force WarmUp to an end
~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//endwu``
Parameters:
  None
Functionality:
  Force the whole WarmUp to an end.
Required permission:
  ``admin:end_round``, requires admin level 2.

Set rounds points (Points repartition)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//pointsrepartition`` / ``//pointsrep``
Parameters:
  * Points per place, top to bottom, separated with either spaces or commas.
Functionality:
  Set the rounds points (points per player and place it ends in an round).
Required permission:
  ``admin:points_repartition``, requires admin level 2.


Server
^^^^^^

Set server name
~~~~~~~~~~~~~~~
Command:
  ``//servername``
Parameters:
  * Server name.
Functionality:
  Changes the server name.
Required permission:
  ``admin:servername``, requires admin level 2.

Set game mode
~~~~~~~~~~~~~
Command:
  ``//mode``
Parameters:
  * Game mode 'ta', 'laps', 'rounds', 'cup' or any script name (e.g. 'Rounds.Script.txt')
Functionality:
  Changes the server game mode script.
Required permission:
  ``admin:mode``, requires admin level 2.

Get/set game mode settings
~~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//modesettings``
Parameters:
  None, or:
  * Setting name
  * New setting value
Functionality:
  Displays a list of current mode settings (no parameters) or changes a setting according with the given parameters.
Required permission:
  ``admin:mode``, requires admin level 2.

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
