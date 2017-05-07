Changelog
=========

0.0.3
-----

Contrib Apps
~~~~~~~~~~~~

**Local records** `pyplanet.apps.contrib.local_records`

* Bugfix #107: Widget showing wrong offset of records. (Not showing own record if just in the first part of >5 recs).


0.0.2
-----

Contrib Apps
~~~~~~~~~~~~

**Local records** `pyplanet.apps.contrib.local_records`

* Bugfix #106: Widget not updating when map changed. Login not found exception.


0.0.1
-----

Core
~~~~

* First implementation of the core.
* First implementation of the CLI tool.


Contrib Apps
~~~~~~~~~~~~

**Admin** `pyplanet.apps.contrib.admin`

* Feature: Basic map functions: skip / restart / add local / remove / erase / writemaplist
* Feature: Basic player functions: ignore / kick / ban / blacklist
* Feature: Basic server functions: set passwords (play / spectator)

**Map list + jukebox** `pyplanet.apps.contrib.jukebox`

* Feature: Display maplist with maps currently on the server
* Feature: Basic jukebox functions: list / drop / add / clear (admin-only)

**Map karma** `pyplanet.apps.contrib.karma`

* Feature: Basic map karma (++ / --)
* Feature: Display who voted what (whokarma)

**Local records** `pyplanet.apps.contrib.local_records`

* Feature: Saving local records
* Feature: Display current first/personal record on map begin (in chat)
* Feature: Display list of records

**Playerlist** `pyplanet.apps.contrib.players`

* Feature: Add join/leave messages.

**MX** `pyplanet.apps.contrib.mx`

* Feature: Add MX maps (//add mx [id(s]).
* Feature: Implement MX API Client.
