Music Server
==============

Information
-----------
Name:
  ``pyplanet.apps.contrib.music_server``
Depends on:
  -
Game:
  All

Features
--------
This app provides the ability to play your own music for all the players in the server.

**Setup:**

Add URLs to the music files you want to play your settings module (base.py) or directory (base.json / base.yaml)
in the ``SONGS = []`` section. The files must be in the .ogg format for maniaplanet to be able to play them.

Commands
--------

Display music list
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``/songlist`` or ``/musiclist``
Parameters:
  None.
Functionality:
  Displays the list of all available songs. Click songs to put them into the playlist.
Required permission:
  None.

Display Playlist
~~~~~~~~~~~~~~~~~~~
Command:
  ``/playlist``
Parameters:
  None.
Functionality:
  Display the playlist. Click songs to drop them from the playlist. Users can only drop the songs the juked themselves.
Required permission:
  None.

Current Song
~~~~~~~~~~~~~~~~~~~
Command:
  ``/song``
Parameters:
  None.
Functionality:
  Prints the Title and Artist of the song currently playing to the chat.
Required permission:
  None.

Play Song
~~~~~~~~~~~~~~~~~~~
Command:
  ``//play``
Parameters:
  ``songname`` URL to music file to be played next.
Functionality:
  Puts the song into the songlist. It will be gone from it on next restart of PyPlanet.
Required permission:
  requires admin level 1



Signal handlers
---------------

Map End
~~~~~~~~~~~~~~
Signal
``pyplanet.apps.core.maniaplanet.callbacks.map.map_end``
Functionality:
  Queue the next song.
