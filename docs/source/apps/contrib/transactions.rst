Transactions
============

Activate with adding ``'pyplanet.apps.contrib.transactions.app.Transactions'`` to your apps.py

Information
-----------
Name:
  ``pyplanet.apps.contrib.transactions``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
Donate, show planets on server and payout players.

Commands
--------

Donate
~~~~~~
Command:
  ``/donate``
Parameters:
  * Amount of planets.
Functionality:
  Donate planets to the server.
Required permission:
  -

Get amount of planets on server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//planets``
Parameters:
  None
Functionality:
  Get planet
Required permission:
  ``admin:planets``, requires admin level 3.

Pay planets to player
~~~~~~~~~~~~~~~~~~~~~
Command:
  ``//pay``
Parameters:
  * Player login
  * Amount of planets
Functionality:
  Pay planets to player.
Required permission:
  ``admin:pay``, requires admin level 3.

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.other.bill_updated``
Functionality:
  Update bill signal
