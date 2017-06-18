Changelog
=========

0.4.2
-----

Core
~~~~

* Improvement: Bump XML-RPC Script API to version 2.2.0.
* Improvement: Show the Round Score build-in ui (nadeo widget) and move it a bit.
* Improvement: Move the build-in warmup ui (nadeo widget) a bit.

Apps
~~~~

* Feature: Add //shuffle and //readmaplist. Both are unsure to work.
* Improvement: Further investigate and report issues related to Dedimania.
* Bugfix: Fixing negative count issue on the info widgets.
* Bugfix: Remove faulty and debug line from dedimania api catch block.
* Bugfix: Properly handle the dedimania response when player is not correct.
* Bugfix: Fixing issues with boolean values and the //modesettings GUI.

0.4.1
-----

Core
~~~~

* Improvement: Add command ignore and /version improvements.
* Improvement: Disable the live infos in the left upper corner (player join/leave, 1st finish).
* Bugfix: Issue with database collate and utf8mb4, nickname parsing issue has been solved.
* Bugfix: Don't auto reload and use different environments for the template engine. Should improve performance very much.
* Bugfix: Ignore unknown login at the chat and UI managers.
* Bugfix: Ignore key interrupt exception trace when stopping PyPlanet while it has got a reboot in the mean time.
* Bugfix: Hide the ALT menu in shootmania, just as it should do since before 0.4.0.
* Bugfix: Fixing issue with checking for updates could result in a exception trace in the console for some installations with older setuptools.
* Bugfix: Fixing an issue that results in fetching data for widget several times while it's not needed (thinking it's per player data when it isn't). (Thanks to Chris92)


Apps
~~~~

* Improvement: Make it able to drive dedimania records on short maps made by Nadeo.
* Improvement: Make the improvement time blue like Nadeo also does in the sector times widget.
* Improvement: Always show nickname of the map author and make it switchable by clicking on it.
* Bugfix: Don't set the time of the spectator as your best time in the sector times widget.
* Bugfix: Problems that could lead to dedimania not being init currently on the map if the map was replayed.
* Bugfix: Hide dedimania if map is not supported.
* Bugfix: Fix the offset issue for the live rankings widget (in TA mode).
* Bugfix: Fix the incorrect number of spec/player count on the top left info widget.


0.4.0
-----

Core
~~~~

* **Breaking**: Refactored the TemplateView to make it able to use player data way more efficient.

  This is a *deprecation* for the method ``get_player_data``. From now on, use the ``get_all_player_data`` or the better ``get_per_player_data``.
  More info: :doc:`/api/views`.

  **The old method will not be called from 0.6.0**

* Feature: UI Overhaul is done! We replaced the whole GUI for a nicer, simple and modern one! With large inspiration of LongLife's posted image (https://github.com/PyPlanet/PyPlanet/issues/223).
* Feature: UI Update queue, Don't make the dedicated hot by sending UI updates in realtime, but queue up and sent every 0,25 seconds. (Performance)
* Improvement: Removing the fix for symbols in nicknames/chat (fix for the maniaplanet dedicated/client issue earlier).
* Improvement: Add analytics.
* Improvement: Don't report several exceptions to Sentry.
* Improvement: Remove SQlite references in code and project skeleton.
* Improvement: Give error message when loaded script is using old style scripted callbacks.
* Improvement: Dynamic future timeouts for script/gbx queries.
* Improvement: Add ManiaScript libs includes in core. Will be expanded, open pull requests if needed!
* Improvement: Adding two new signals for players when entering spec/player slot.
* Bugfix: Adding several investigation points to send more data about problems that occur for some users.


Apps
~~~~

* **Breaking**: Refactor the MapInfo app to Info app. Adding new features: Server and general info on top left corner.

  This requires a config change:
  Change ``pyplanet.apps.contrib.mapinfo`` into ``pyplanet.apps.contrib.info`` and you are done!

  **The old app will be removed in 0.6.0**

* Feature: **New App**: Shootmania Royal Dynamic Point Limit is here! Add it with ``pyplanet.apps.contrib.dynamic_points``.
* Feature: **New App**: Trackmania Checkpoint/Sector time widget is here! Add it with ``pyplanet.apps.contrib.sector_times``.
* Feature: Change modesettings directly from the GUI (//modesettings).
* Improvement: Apply the new UI Overhaul to all apps.
* Improvement: Add message when dedimania records are sent.
* Improvement: Improve the dedimania error handling even better.
* Improvement: Notice when map is not suited for dedimania records.
* Improvement: Several performance improvements on the dedimania and localrecords apps.
* Improvement: Add dynamic actions to map list, such as deletion of maps.
* Improvement: Modesettings list is ordered by name by default now.
* Bugfix: Adding several investigation points to send more data about problems that occur for some users.
* Bugfix: Trying to sent dedi records when dedimania isn't initialized bug is solved.
* Bugfix: Prevent double message of dedimania record when switching game modes.
* Bugfix: Fixing double local records (or investigate more if it still occurs).



0.3.3
-----

Core
~~~~

* Bugfix: Ignore errors with unknown login for ui updates. (means the player left).


Apps
~~~~

* Bugfix: Fixing issues with dedimania and unsupported maps.
* Bugfix: Fixing issues with dedimania and replays.
* Bugfix: Fixing issues with local records widget showing the wrong offset.
* Bugfix: Fixing issues with local records and double records.
* Improvement: Some not visible improvements to the local record widget logic.

0.3.2
-----

Core
~~~~

* Bugfix: Not properly sending and handling mode changes.
* Bugfix: Several errors in handling the callbacks in shootmania


Apps
~~~~

* Bugfix: Fixing issue with removing or erasing maps.
* Improvement: Dedimania now also works in cup mode.
* Feature: Add //replay command for admins, make it able to juke the current map for non-players (ops and admins)


0.3.1
-----

Core
~~~~

* Improvement: Multiple namespaces per command + improve help.
* Improvement: Hide the alt menu in shootmania when having a window in the middle.
* Improvement: Add method to retrieve map by index.
* Bugfix: Save boolean in the //settings
* Bugfix: Fixing issue with writing the map list.
* Bugfix: Handling of fetching player in a callback for shootmania.
* Bugfix: Several fixes for shootmania modes.


Apps
~~~~

* Improvement: Make dedimania record message shorter.
* Bugfix: Double prefix in leave messages.
* Bugfix: Dedimania nickname fetching gave error. Sometimes the widget didn't work properly.
* Bugfix: Improve error handling in Dedimania.
* Bugfix: Fixing issue with write map list (admin part of it).
* Bugfix: Don't display the time of the author when in shootmania


0.3.0
-----

Core
~~~~

* Feature: Refactor the app config class so you can define apps in __init__.py and use shorter configuration, (backward compatible for current contrib apps).
* Feature: Signals runs with gather mode (parallel) now. Makes this way more faster!
* Feature: Add save hook to setting object.
* Feature: Chat contrib component, for shorter syntax at sending and preparing chat messages.
* Feature: Refactor the GBX component, for shorter syntax at sending and preparing Gbx Methods.
* Feature: Make it able to change the UI Properties from the games
* Feature: Add 'suggestion or bug' report button.

* Improvement: Unknown command message.
* Improvement: Makes it faster to display local records.
* Improvement: Refactor the local record code.


Apps
~~~~

* Feature: Add Live Rankings app (beta). Add it to your apps.py!
* Feature: Add chat announce limit in local and dedi records.

* Improvement: Autosave matchsettings on insertion of map.
* Improvement: Hide dedimania widget on downtime.
* Improvement: Better error handling in dedimania app.

* Bugfix: Fixing issue with displaying WhoKarma list.
* Bugfix: Fixing path issues in MX app.


0.2.0
-----

Core
~~~~

* Feature: Improved performance with the all new Performance Mode. This will improve performance for a player threshold that is freely configurable.
* Feature: Technical: Add option to strip styles/colors from searchable column in listviews.
* Feature: Technical: Add shortcut to get an app setting from global setting manager.

* Improvement: Improve log color for readability.

* Bugfix: Fixing issue with integer or other numeric values and the value 0 in the //settings values.
* Bugfix: Replace invalid UTF-8 from the dedicated response to hotfix (dirty fix) the bug in client with dedicated communication.

Apps
~~~~

* Feature: New app: Transactions: Features donations and payments to players as the actual planets stats. Activate the app now in your apps.py!!
* Feature: Map info shows nickname of author if the author nickname is known.
* Feature: /list [search] directly searching in map list.
* Feature: Implement //modesettings to show and change settings of the current mode script.
* Feature: Restrict karma voting to count after the player finishes the map for X times (optional).
* Feature: Apply the performance mode improvements to the local and dedimania records widgets.
* Feature: Add command to restart PyPlanet pool process. //reboot

* Improvement: Changed dedimania record text chat color.
* Improvement: Changed welcome player nickname default color (white).
* Improvement: Reduced length of record chat messages.
* Improvement: Add player level name to the join/leave messages.

* Bugfix: Jukebox current map gives errors and exceptions.
* Bugfix: Ignore color and style codes inside /list searching.
* Bugfix: Some small improvements on widgets (black window behind local/dedi removed and more transparent)

0.1.5
-----

Core
~~~~

* Bugfix: Fixing several issues related to the connection and parsing of the payload.
* Bugfix: Fixing issue with the BeginMatch callback.
* Bugfix: Change issues related to the utf8mb4 unicode collate (max index lengths).

Apps
~~~~

* Bugfix: Fixing several issues with the dedimania app.
* Bugfix: Fixing issue with local and dedimania records being saved double (2 records for 1 player). (#157).
* Bugfix: Fixing several exception handling in dedimania app.


0.1.4
-----

Core
~~~~

* Bugfix: Undo locking, causing freeze.

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
