PayPal
=======

Information
-----------
Name:
  ``pyplanet.apps.contrib.PayPal``
Depends on:
  ``core.maniaplanet``
Game:
  TrackMania, ShootMania

Features
--------
This app provides the display of a PayPal logo and the possibility to embed a donation link behind it.

**Setup:**

1. Create the PayPal donation link for you server account
2. Start PyPlanet with this app enabled.
3. Type //settings and fill the PayPal related field (Donation URL)

Your donation URL should now be embedded in the PayPal logo.

Signal handlers
---------------

Player connect
~~~~~~~~~~~~~~
Signal
``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displaying widget
