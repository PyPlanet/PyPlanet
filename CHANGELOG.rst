Changelog
=========

0.5.2
-----

Core
~~~~

* Improvement: Disable writing log files by default from 0.5.2.
* Improvement: Move logo and clock down so it doesn't interfere with the spectator icon.

* Bugfix: Logging on windows should be fixed now.
* Bugfix: Issue with multiple users editting modesettings or PyPlanet settings at the same time.

Apps
~~~~

* Feature: Add zero karma folder (auto-folder)
* Feature: Added settings to enable or disable specific chat votes.
* Feature: Add //cancelcall (//cancelcallvote) for cancelling a call vote as an admin.
* Feature: Add //pass to pass a chat vote with your admin powers.
* Feature: Add button to add current map to folder on the folder list.

* Improvement: Change chat color of the chat vote lines.
* Improvement: Disable callvotes when chatvotes is turned on (made setting for this as well).

* Bugfix: Only show the folders of the user when adding maps to a folder.
* Bugfix: Fix error when player has not been online and users trying to get the last on date of the player.
* Bugfix: Remove unique index on the folder name so folders can have the same name over all. (auto-migration made).
* Bugfix: Fix bug that prevented added maps to be auto-juked.


0.5.1
-----

Core
~~~~

* Bugfix: Fix for Windows users and import error.


0.5.0
-----

Core
~~~~

* **Breaking**: App context aware signal manager.

  This is a *deprecation* for the property ``signal_manager`` of the ``instance``. This means that ``self.instance.signal_manager``
  needs to be replaced by ``self.context.signals`` to work with the life cycle changes in 0.8.0.
  More info: https://github.com/PyPlanet/PyPlanet/issues/392

  **The old way will break your app from version 0.8.0**

* Feature: Add multiple configuration backends. You can now use JSON or YAML as configuration as well. This is in a beta
  stage and can still change in upcoming versions. See the documentation for usage.
* Feature: Add logging to file option for starting PyPlanet. You can set this up inside of your settings `base.py`.
  More information can be found in the documentation for configuring PyPlanet.
* Feature: Add detach switch to the PyPlanet starter so it can fork itself to the background and write a PID file.
  More information can be found in the documentation for starting PyPlanet.
* Feature: Add player attributes that can be set by apps for caching or maintaining user settings or data during the session. (Technical)
* Feature: Add migration script for eXpansion database. Look at the manual on http://www.pypla.net/en/stable/convert/index.html for more information.

* Improvement: Retry 5 times when connecting to the dedicated server, making it possible to start both at the same time.
* Improvement: Update library versions.
* Improvement: Add minimum required version of the dedicated server to prevent starting PyPlanet for non-supported dedicated versions.
* Improvement: Only check for stable new versions. Now check for releases instead of tags on Github.
* Improvement: Let the list view skip 10 pages buttons skip to end or begin when less than 10 pages difference. (Thanks @froznsm)
* Improvement: Add online players login list in the player_manager. (Technical)

* Bugfix: Fixing issue with the release checker.
* Bugfix: Fixing the link to the upgrade documentation page (Thanks to @thefifthisa).
* Bugfix: Only handle player info change event when this player is still on the server to prevent errors.
* Bugfix: Handle exception when the server initiated a callvote (Thanks to @teemann).
* Bugfix: Correctly handle None column values when searching and/or sorting generic lists.
* Bugfix: Correctly handle non-string column values when searching and/or sorting generic lists.
* Bugfix: Refresh and fixed the player and spectator counters.


Apps
~~~~

* NEW: Best CPS Widget for Trackmania, shows the best times per checkpoint above the screen.
  Add the new app to your apps.py: `'pyplanet.apps.contrib.best_cps'`. More info on the documentation pages of the app. (Big thanks to @froznsm)

* NEW: Clock Widget, shows the local time of the players computer on the PyPlanet logo.
  Add the new app to your apps.py: `'pyplanet.apps.contrib.clock'`. More info on the documentation pages of the app. (Big thanks to @froznsm)

* NEW: Chat-based Vote App, want to have votes in the chat instead of the callvotes? Enable this app now!
  Add the new app to your apps.py: `'pyplanet.apps.contrib.voting'`. More info on the documentation pages of the app.

* Feature: Add folders to the /list interface. There are two types of folders, automatic folders based on facts and manual per player/admin folders.
* Feature: Add folders for karma related information when karma app is enabled.
* Feature: Add folder for newest maps (added within 14 days).
* Feature: Add spectator status in the /players list.
* Feature: Add /scoreprogression command to see your current score progressions statistics on the current track.
* Feature: Add team switch commands (//forceteam and //switchteam) to the admin app.
* Feature: Add warning command (//warn) and alert to the admin app to warn players.
* Feature: Add the MX link of the current map to the logo left from the map name.
* Feature: Add setting to directly juke after adding map from MX or local (defaults to on).
* Feature: Add //blacklist and //unblacklist to the admin app.

* Improvement: Applied context aware signal manager everywhere.
* Improvement: Moving logic to view in dedimania app.
* Improvement: Adding setting to juke map after //add (mx and local) the map. Enabled by default!
* Improvement: Adding help text to jukebox app command.
* Improvement: Remove workaround for the fixed dedicated issue caused problems with the dedimania app.
* Improvement: Only show login in /list for now as it was causing inconsistency.
* Improvement: Check if the player is online before taking admin actions like kicking the player.
* Improvement: Refactor logic of viewing dedimania records to the desired view class. (Technical)
* Improvement: Further investigate dedimania problems for some specific players. Internal cause is known, exact reason not yet, we will further investigate this issue.

* Bugfix: Make sure to skip jukeboxed map when it's deleted from the server.
* Bugfix: Fix the double live rankings entry when changing nickname.
* Bugfix: Check if we have data to compare before calculating CP difference in the live rankings widget.
* Bugfix: Local record widget display fix when player joined during a very specific time that causes it to not display to the user.


0.4.5
-----

Core
~~~~

* Feature: Add ManiaControl convert script. See documentation on converting from old controller for instructions.
* Improved: Add documentation on how to convert to the right database collation.

Apps
~~~~

* Bugfix: Fixing issue in the Dymanic Pointlimit app that results in 3 settings having the same key name.

0.4.4
-----

* Feature: Add UAseco convert script. See documentation on converting from old controller for instructions.
* Improved: Updated libraries and dependencies.
* Bugfix: Catch error when server initiated callvote, thanks to @teemann.
* Bugfix: Fix the release/update checker.

0.4.3
-----

Apps
~~~~

* Bugfix: Fix issue with switching to custom script (lower case not found), specially teams mode.

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

  **The old method will not be called from 0.7.0**

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

  **The old app will be removed in 0.7.0**

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
