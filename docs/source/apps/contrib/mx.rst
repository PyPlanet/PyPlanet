ManiaExchange / TrackmaniaExchange
==================================

Information
-----------
Name:
  ``pyplanet.apps.contrib.mx``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania / Trackmania Next / Shootmania

Features
--------
Adding maps from ManiaExchange or TrackmaniaExchange (depending on the game).
The prefix of the commands can be either ``mx`` or ``tmx`` depending on your game. For Maniaplanet games it will
be ``mx``.

Commands
--------

Add map(s) from MX/TMX
~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//add mx`` or ``//mx add`` or ``//tmx add``
Parameters:
  * ManiaExchange/TrackmaniaExchange ID(s). One or more with space between it.
Functionality:
  Adding maps from ManiaExchange/TrackmaniaExchange to the server.
Required permission:
  ``mx:add_remote``, requires admin level 3.


Search maps on MX/TMX
~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//mx search`` or ``//tmx search``
Parameters:
  -
Functionality:
  Search/browse for maps on MX/TMX.
Required permission:
  ``mx:add_remote``, requires admin level 3.


Add mappack from MX/TMX
~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//mxpack add`` or ``//tmxpack add``
Parameters:
  * ManiaExchange/TrackmaniaExchange Pack ID.
Functionality:
  Adding maps form a specific mappack on ManiaExchange/TrackmaniaExchange to the server.
Required permission:
  ``mx:add_remote``, requires admin level 3.


Search mappacks on MX/TMX
~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//mxpack search`` or ``//tmxpack search``
Parameters:
  -
Functionality:
  Search/browse for mappacks on MX/TMX.
Required permission:
  ``mx:add_remote``, requires admin level 3.


Check maplist for updates
~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//mx status`` or ``//tmx status``
Parameters:
  -
Functionality:
  Check for updated maps on MX/TMX.
Required permission:
  ``mx:add_remote``, requires admin level 3.


Get current map info
~~~~~~~~~~~~~~~~~~~~
Command:
  ``/mx info`` or ``/tmx info``
Parameters:
  -
Functionality:
  Get information about the current map from the MX/TMX database.
Required permission:
  -
