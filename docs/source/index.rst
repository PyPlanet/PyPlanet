Welcome to PyPlanet's documentation!
====================================

..  image:: /_static/logo/pyplanet-sm.png
    :scale: 30%
    :align: right

PyPlanet is a Maniaplanet/Trackmania Dedicated Server Controller that works on Python 3.6 and later.
Because Maniaplanet/Trackmania is using a system that can be event based we use AsyncIO to provide
an event loop and have simultaneously processing of received events from the dedicated server.

**Features**:

* Core: Super fast and 'event' driven based on Python 3.5 ``asyncio`` eventloop.
* Core: Stable and well designed core and apps system. (Inspired by Django).
* Core: All apps will handle the game experience.
* Core: Adjustable settings for all your apps.
* Core: Supports **Trackmania 2**, **Trackmania 2020** and **Shootmania**, **Scripted only!**
* App: Local Records, including widget + list.
* App: Dedimania Records, including widget + list.
* App: Admin Commands, Providing with basic commands and control for maintaining your server.
* App: Admin Toolbar, Providing mostly used admin functions within a few clicks.
* App: Karma, Let your players vote on your maps! Includes MX Karma integration.
* App: Jukebox, Let your players 'juke' the next map.
* App: ManiaExchange, Simply add your maps directly from Mania-Exchange.
* App: Players, This app shows messages when players join and leave.
* App: Transactions, Donate planets to the server, show number of planets on server and pay out players.
* App: Live Rankings, Show the live rankings of the game mode. (Trackmania).
* App: Sector Times, Compare your checkpoint time against your local or dedimania record. (Trackmania).
* App: Dynamic Pointlimit, Royal point limit adjustment based on the number of players. (Shootmania Royal).
* App: CP Times, Show the best checkpoint times on top of your screen.
* App: Chat based voting, No more uncontrollable and unfair Call Votes. Use chat based voting.
* App: Vote to extend the TimeAttack limit instead of restarting the map! Extend-TA© command and voting is awesome!
* App: Waiting Queue, no more unfair and spamming of the join button, fairly queue spectators to join your full server.
* App: Add links to your PayPal donate page or Discord server.

Do you want to install PyPlanet, head towards our :doc:`Getting Started Manual </intro/index>`.
Want to see PyPlanet in action, head to :ref:`screenshots-ref`.

The code is open source, and `available on GitHub`_.

.. _available on GitHub: https://github.com/PyPlanet

The main documentation for the site is organized into a couple sections:

* :ref:`user-docs`
* :ref:`app-docs`
* :ref:`about-docs`

Information about development of apps and the core is also available under:

* :ref:`dev-docs`


..  _user-docs:

..  toctree::
    :maxdepth: 2
    :caption: User Documentation

    intro/index
    intro/configuration
    intro/starting
    intro/upgrading
    convert/index
    howto/index


.. _app-docs:

..  toctree::
    :maxdepth: 1
    :glob:
    :caption: Apps Documentation

    apps/contrib/admin
    apps/contrib/ads
    apps/contrib/best_cps
    apps/contrib/clock
    apps/contrib/dedimania
    apps/contrib/dynamic_points
    apps/contrib/dynatime
    apps/contrib/jukebox
    apps/contrib/karma
    apps/contrib/live_rankings
    apps/contrib/local_records
    apps/contrib/mapinfo
    apps/contrib/music_server
    apps/contrib/mx
    apps/contrib/players
    apps/contrib/queue
    apps/contrib/sector_times
    apps/contrib/transactions
    apps/contrib/voting
    apps/contrib/funcmd
    apps/core/statistics
    apps/core/pyplanet


.. _dev-docs:

..  toctree::
    :maxdepth: 2
    :caption: Developer Documentation

    architecture/index
    apps/index
    signals/index

    api/index


.. _about-docs:

..  toctree::
    :maxdepth: 1
    :caption: About PyPlanet

    support
    privacy
    changelog
    todo


Some thoughts from experts
==========================

.. raw:: html

  <iframe src="https://clips.twitch.tv/embed?clip=MagnificentHappyMarrowHeyGuys&autoplay=false" width="640" height="360" frameborder="0" scrolling="no" allowfullscreen="true"></iframe>

|
|


.. _screenshots-ref:

Screenshots
===========

.. image:: /_static/screenshots/tm_1.jpg

.. image:: /_static/screenshots/tm_2.jpg



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Links
=====

| Documentation: http://pypla.net/
| GitHub: https://github.com/PyPlanet/PyPlanet
| PyPi: https://pypi.python.org/pypi/pyplanet
