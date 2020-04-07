Advertisements
==============

Information
-----------
Name:
  ``pyplanet.apps.contrib.ads``
Depends on:
  -
Game:
  All

Features
--------
This app provides buttons, banners and other advertisements assets. For example it shows a Discord logo or a PayPal button.
The app has the following features:
- Show Discord join button.
- Show how many users online in Discord.
- Show PayPal donate button.
- Random messages at specific times.

**Setup Discord:**

1. Get your discord join link and make sure it does not expire.
2. Get your discord server ID. (you might need to enable developer settings)
3. Enable the widget of your discord server in the server settings.
4. Start PyPlanet with this app enabled.
5. Type //settings and edit two discord related fields (join URL and ID)

**Setup PayPal:**

1. Create the PayPal donation link for you server account
2. Start PyPlanet with this app enabled.
3. Type //settings and fill the PayPal related field (Donation URL)

**Random Message:**

1. Enter the random messages by editing //settings (find the random messages entry).
   Every line represents one message, you can use any formatting in the messages!
2. Optionally edit the random messages interval

Commands
--------

Display Discord Server Info
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Command:
  ``/discord``
Parameters:
  None.
Functionality:
  Displays the number of users and bots on the server.
Required permission:
  None.

Display PayPal Link
~~~~~~~~~~~~~~~~~~~
Command:
  ``/paypal``
Parameters:
  None.
Functionality:
  Display the PayPal link in chat.
Required permission:
  None.

Signal handlers
---------------

Player connect
~~~~~~~~~~~~~~
Signal
``pyplanet.apps.core.maniaplanet.callbacks.player.player_connect``
Functionality:
  Displaying widgets
