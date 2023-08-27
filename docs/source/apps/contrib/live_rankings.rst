Live Rankings
=============

Information
-----------
Name:
  ``pyplanet.apps.contrib.live_rankings``
Depends on:
  ``core.maniaplanet``
Game:
  Trackmania

Features
--------
This app enables the live rankings widget for the game modes:

- Laps (Live cp statistics).
- Rounds (Match sum of points).
- TimeAttack (Top times of players).
- Cup & Team (Points gathered).

It can also be used to replace the default in-game 'Race Rankings' widget in Rounds, Cup and Team modes.
While the default widget only displays the first seven finishers, this widget works like the others: displaying more finishers and mainly those around the player.

Installation
------------

Just add this line to your ``apps.py`` file:

.. code-block:: python

  APPS = {
    'default': [
      '...',
      'pyplanet.apps.contrib.live_rankings',  # Add this line.
      '...',
    ]
  }


Settings
--------

Amount of widget entries
~~~~~~~~~~~~~~~~~~~~~~~~
Setting:
  ``rankings_amount``
Functionality:
  Sets the amount of entries to be displayed in the Live & Race Rankings widget (minimum: 15).
Default value:
  ``15``

Display in-game race rankings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Setting:
  ``nadeo_live_ranking``
Functionality:
  Shows the in-game provided race rankings widget (overridden by ``race_live_ranking``).
Default value:
  ``True``

Display race rankings
~~~~~~~~~~~~~~~~~~~~~
Setting:
  ``race_live_ranking``
Functionality:
  Shows the PyPlanet-provided race rankings widget (overrides ``nadeo_live_ranking``).
Default value:
  ``True``


Commands
--------

-

Signal handlers
---------------

Map begin
~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.map.map_start``
Functionality:
  Clears rankings and widget

Player finish
~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.finish``
Functionality:
  Process and update widget.

Player waypoint
~~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.waypoint``
Functionality:
  Process and update widget.

Player give up
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.give_up``
Functionality:
  Set the time to DNF in specific modes.

Player connect
~~~~~~~~~~~~~~
Signal:
  ``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Display widget.

Scores
~~~~~~
Signal:
  ``pyplanet.apps.core.trackmania.callbacks.scores``
Functionality:
  Update the widget with the driven scores.
