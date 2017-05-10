Changelog
=========

0.1.3
-----

Apps
~~~~

* Bugfix: Fixing issue in dedimania causing crash.

0.1.2
-----

Core
~~~~

* Bugfix: Filter out XML parse error of Dedicated Server (#121).
* Bugfix: Give copy of connected players instead of a reference to prevent change of list when looping (#117).
* Bugfix: Fixing issue when player rapidly connects and disconnects, giving error (#126 & #116).


Apps
~~~~

* Bugfix Karma: Fixing whokarma list not displaying due to error (#122 & #118).
* Bugfix Dedimania: Reconnection issues (#130).
* Improvement Local Records: Improve performance on sending information (chat message) on large servers. (#139).
* Improvement Dedimania Records: Improve performance on sending information (chat message) on large servers. (#139).
* Improvement Dedimania Records: Improve the error reporting and implement shorter timeout + retry procedure (#139).


0.1.1
-----

Core
~~~~

* Fixing issue with creating migrations folder when no permission.


0.1.0
-----

Core
~~~~

* Add new fields to the ``game`` state class.
* Refresh the ``game`` infos every minute.


Contrib Apps
~~~~~~~~~~~~

* NEW: Dedimania App: Adding dedimania integration and widget.


0.0.3
-----

Contrib Apps
~~~~~~~~~~~~

* Bugfix Local Records: Widget showing wrong offset of records. (Not showing own record if just in the first part of >5 recs) (#107).


0.0.2
-----

Contrib Apps
~~~~~~~~~~~~

* Bugfix Local Records: Widget not updating when map changed. Login not found exception. (#106).


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
