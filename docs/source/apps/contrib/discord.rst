Discord
=======

Information
-----------
Name:
  ``pyplanet.apps.contrib.discord``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
This app provides access to a given discord server. It can show how many users and bots are online in said server.

**Setup:**

1. Get your discord join link and make sure it does not expire.
2. Get your discord server ID. (you might need to enable developer settings)
3. Enable the widget of your discord server in the server settings.
4. Start PyPlanet with this app enabled.
5. Type //settings and edit two discord related fields (join URL and ID)

If you do not edit these fields it will resort to the Trackmania discord.

Commands
--------

Display Server Info
~~~~~~~~~~~~~~~~~~
Command:
  ``/discord``
Parameters:
  None.
Functionality:
  Displays the number of users and bots on the server.
Required permission:
  None.

Signal handlers
---------------

Player connect
~~~~~~~~~~~~~~
Signal
``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displaying widget
