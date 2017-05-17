Live Rankings
=============

Information
-----------
Name:
  ``pyplanet.apps.contrib.live_rankings``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania

Features
--------
This app enables the live rankings widget for the game modes:

- Laps (Live cp statistics).
- Rounds (Match sum of points).
- TimeAttack (Top times of players).
- Cup & Team (Points gathered).


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
