Changelog
=========

0.9.14
------

Core
~~~~

* Improvement: Several libs updated.
* Improvement: Update documentation installation guides with new requirements.
* Improvement: Write PID file also without detaching process.
* Improvement: Updated screenshots on the documentation page.

* Bugfix: Fix maximum lines in settings textarea fields.
* Bugfix: Fix the visibility of widgets in TM2020 (z-index increase).


Apps
~~~~

* Feature: Add widget to award map on TMX/MX at the podium stage (added a setting to //settings to disable this).

* Improvement: Allow masteradmins to remove public maps of other admins.
* Improvement: Disable chat votes when public chat is disabled.
* Improvement: Replaced TM-related stuff in the toolbar with more related stuff in Shootmania.

* Bugfix: Fix bug when MX Karma is down to ignore everything with MX karma.
* Bugfix: Fix folder view not refreshing when changes are made.
* Bugfix: Handle error with SSL certificate in MX karma app.
* Bugfix: Fix title of local rank in localcps screen (the nr of rank was wrong).


0.9.13
---------------------

Core
~~~~

* Bugfix: Fix issue with Jinja2 and MarkupSafe (MarkupSafe version not locked).


0.9.11 & 0.9.12 (30 July 2021)
------------------------------

Core
~~~~

* Feature: Support for Royal mode in TM 2020.

* Improvement: Several libs updated.
* Improvement: Removed apyio==0.2.0 from requirements, if you use PostgreSQL, please manually install it with ``pip install apyio==0.2.0``

* Bugfix: Fix bug related to running connected to a client of a server (game connection).


0.9.10 (22 March 2021)
----------------------

Core
~~~~

* Improvement: Several libs updated.

* Bugfix: Showing mapinfo from Nadeo on Shootmania (hidden again)

Apps
~~~~

* Bugfix: Revert the controller 'hide GUI' feature.


0.9.6 + 0.9.7 + 0.9.8 + 0.9.9 (21 February 2021)
------------------------------------------------

Core
~~~~

* Improvement: Add support for UI properties in TM2020.
* Improvement: Add support for Echo callback.
* Improvement: Add support for several new TM2020 callbacks.
* Improvement: Increase the supported script modes version.

* Bugfix: Issue resolved for checking the mode_requirement in apps.

Apps
~~~~

* Feature: Adding dynatime app! Add it in your apps.py to enable.
* Feature: Add limit for extending the timelimit, setting has been added to //settings.
* Feature: Mania-Exchange random maps function.

* Improvement: Adjust the API urls of Mania-Exchange.
* Improvement: Update UI support for controllers.
* Improvement: Current CPs improvements and enable for TM2020.
* Improvement: Don't show delete icon when not having the right permissions (in map list and records list).

* Bugfix: Fix for TeamMode where the quad is fully colored.
* Bugfix: Fix for fun commands usage in wrong games and when muted.
* Bugfix: Fix retrieval of current players/spectators in Dedimania API update loop
* Bugfix: Fixing issues with retrieving dedimania records when switching modes.
* Bugfix: Resolve typos in several locations.
* Bugfix: Resolve issues with MX on MP.
* Bugfix: Resolve issues with dedimania on MP.


0.9.5 (28 October 2020)
-----------------------

Core
~~~~

* Bugfix: Fixing issues with collecting checkpoint data on finish callback. Related to the TM2020 checkpoint comparison issue.

Apps
~~~~

* Improvement: Improving the external link to the map page on MX/TMX in the upper right corner.
* Improvement: Move the sector times widget in TM2020 to the left of the time counter.
* Improvement: Change icon of the map info widget.
* Bugfix: Fixing the issue with the checkpoint comparison in TM2020. Also put in a failsafe to not show corrupted local records from the past.
* Bugfix: Fixing the issue with displaying the incorrect checkpoint counter the sector times widget.
* Bugfix: Fixing the issue with sending the permission error message of deleting a record to all players (now send it only to the player that clicked).


0.9.4 (16 October 2020)
-----------------------

Core
~~~~

* Improvement: Add widget visibility toggle in player toolbar to promote F8.
* Bugfix: Adding local maps will refresh the list from now on.
* Bugfix: Fix the name of the teams script for TM2020, making //mode teams work now.
* Bugfix: Fixing the issue with not recording any scores in TM2020 resulting in the minimum finish before karma vote issue.

Apps
~~~~

* Improvement: Ability to copy the player login from any player list.
* Bugfix: Fixing live rankings in Laps mode.
* Bugfix: Small exception resolved with adding duplicated map.
* Bugfix: Fix issue with Karma being Nan in the advanced list and fixing issues with loading the advanced list.

* Known issue: Fixing the issue with CP comparison widget in TM2020.


0.9.3 (10 September 2020)
-------------------

Core
~~~~

* Feature: Add guestlist support. //addguest, //removeguest and adding settings and commands to save it to disk.
* Improvement: Add mode shortcuts for TM2020, from now you can do //mode ta etc.

Apps
~~~~

* Feature: Add support for sector times in TM2020.
* Feature: Add support for live rankings in TM2020.
* Improvement: Add support for //endround in TM2020.
* Bugfix: Fixing issue with map info from TMX.
* Bugfix: Fixing issue with the minimal finishes setting in the karma app.
* Bugfix: Fixing issue with inserting maps on adding from TMX.
* Bugfix: Fixing issue with NaN in advanced list.


0.9.2 (8 July 2020)
-------------------

Apps
~~~~

* Improvement: Add full support for TMX Trackmania Exchange.
* Bugfix: Fixing issues with the random messages in the ads app.


0.9.1 (6 July 2020)
-------------------

Apps
~~~~

* Feature: Claim admin rights by /claim [token]. Check the console for the token.
* Improvement: Adding semi-support for TMX Trackmania Exchange. More support coming later when the API becomes available.
* Bugfix: Fixing issues with adding maps for the new Trackmania (2020).


0.9.0 (1 July 2020)
-------------------

Core
~~~~

* Feature: Support for the new Trackmania.
* Bugfix: Fixing issue with parsing target player in spectator status in the player change callback.

Apps
~~~~

* Bugfix: CP Difference bugfix for spectating users.


0.8.2 (23 May 2020)
-------------------

Core
~~~~

* Bugfix: Fixing issue with the non-updating widgets when performance mode is activated for several apps.

0.8.1 (18 May 2020)
-------------------


Apps
~~~~

* Bugfix: Fixing issue with dedimania and retrying too much (revert new retry mechanism).
* Bugfix: Temporary fix: Revert the live-rankings as it shows incorrect data during warm-ups.
* Bugfix: Move the donation widget to the left in Shootmania.

0.8.0 (13 May 2020)
-------------------

Core
~~~~

* Feature: Activated Apps lifecycle, enabling and disabling apps on the fly depending on it's requirements.
* Feature: Add player toolbox/toolbar. You can disable this with a setting in //settings in-game.
* Feature: Add CP Comparison to find the best checkpoints by using the best checkpoint times of all local records (/cpcomparison).

* Improvement: Dropping Python 3.5 support!
* Improvement: Add //helpall and /helpall for a detailed list of commands!
* Improvement: Only commands that you have permission for will be listed in //help
* Improvement: Remove the deprecated ``instance.signal_manager``.
* Improvement: Add deprecated warning for ``get_player_data`` method.
* Improvement: Improve error reporting when an app failed loading.
* Improvement: Check for platform versions, check if Python is compatible with the PyPlanet installation.
* Improvement: Add support for list/set typed settings.
* Improvement: Add a z-index to different widgets so it will be correctly visible on the podium stage.
* Improvement: Improve list visibility on Shootmania based games.
* Improvement: Add new version of //call with Graphical Interfaces.

* Bugfix: Fixing issue with an empty command input (/ without any text) resulting in executing the last registered command.
* Bugfix: Fixing issue with converting from UAseco when the filename is empty (from a previous XAseco installation).
* Bugfix: Crash with very long map names. Now truncating map names to the maximum allowed length in the database.


Apps
~~~~

* New App: Added Fun Commands app with /gg, /nt, /n1, /ragequit, etc. Add ``pyplanet.apps.contrib.funcmd`` to your apps config.

* Feature: Implemented Emoji Chat toolbar into the fun commands app. Disable with //settings.
* Feature: Add donation widget to the transactions app. On by default, only showing at podium. Change to always with //settings.
* Feature: Add random messages to the Ads app. Add messages and change the interval with //settings.
* Feature: Add gear indicator to the sector_times app, only works in Stadium based games. Enabled by default, disable with //settings.
* Feature: Add points retrieved to the live rankings widget, replacing the build-in finish widget, only works in rounds-based modes.

* Improvement: Make sure all contrib apps don't use ``get_player_data`` anymore.
* Improvement: Decrease size of the AD buttons (Discord and PayPal buttons).
* Improvement: Move the checkpoint difference widgets a bit higher so it doesn't block the view so much (sector_times app).
* Improvement: Improve the retry mechanism of Dedimania during connection issues.
* Improvement: Make sure that updated maps with MX will reappear in the map folders.
* Improvement: Switch the dedimania widget with liveranking and currentcps widgets if dedimania widget is not visible.

* Bugfix: Using the map name from MX if the Gbx map name is not provided by MX.
* Bugfix: Fixing issue with MX update check on Shootmania.
* Bugfix: Show a warning when a map might fail with dedimania due to the size of the embedded blocks.
* Bugfix: Ignore invalid checkpoint times in the best cps widget.


0.7.4 (04 March 2020)
---------------------

Apps
~~~~

* Bugfix: Fixing issue with the MX update dialog and it's internal logic.


0.7.3 (02 March 2020)
---------------------

Core
~~~~

* Bugfix: Make sure the libraries also work for older Python versions (3.5.x).


0.7.2 (02 March 2020)
---------------------

Core
~~~~

* Improvement: Python 3.8.x support!
* Improvement: Update libraries used.
* Improvement: Better error handling for loading configuration/settings files.
* Bugfix: Make sure the MX-id is properly extracted and inserted into the database.

Apps
~~~~

* Feature: Add MX map update window. Access it with //mx status. You can update your maps when there are any available updates.
* Improvement: Add dedimania link to the dedimania page in the chat message and the record list.
* Improvement: Add alias for the command /mapfolders: /mf.
* Improvement: Add alias for the MX search: //mx list and //mxpack list.
* Improvement: Improve the error messages from a failing Dedimania service.
* Bugfix: Make sure the queue app is inactive when the server is password protected.
* Bugfix: Make sure admins can't kick/ban/blacklist admins at the same level or higher.


0.7.1 (23 October 2019)
-------------------------

Core
~~~~

* Bugfix: External map changes are detected wrongly resulting in performance impact in map change on large servers. This issue has been resolved.



0.7.0 (05 October 2019)
-------------------------

Core
~~~~

* **Breaking**: Removed the deprecated ``app.mapinfo``.

* Feature: Keeping track of the MX-id in the database (Database Migration is executed at first startup, no action required for this).
* Feature: Keep track of the total donations and total playtime of the players. Show it with ``/topactive`` and ``/topdons``.

* Improvement: Upgrade several external libraries.
* Improvement: Support for the latest XMLRPC Scripted version and latest dedicated version. (Min. dedicated is now set to 2018-02-09_16_00).
* Improvement: Improve the cleanup and initial reset of the UI Properties.
* Improvement: Changed the key to show/hide some widgets from F7 to F8.
* Improvement: Added one missing scripted event handler for Shootmania.
* Improvement: Update the maplist when a change is detected by the server (useful when adding/removing maps in another tool).

* Security: Update some libraries to fix some security issues (none of which were critical).

* Bugfix: When a map is removed it previously didn't always got removed from the /list view, this has been fixed.

Apps
~~~~

* New App: Integrated the Current CPS App from Teemann into the bundled apps (will get a refactor later on).

* Feature: Add MX Info command ``/mx info``.
* Feature: Add command to show/hide the admin toolbar ``//toolbar``.
* Feature: Add a setting to disable/enable juking maps by players.
* Feature: Add voting widget (displaying buttons when a vote is ongoing).
* Feature: Add support for MX MapPacks. ``//mxpack search`` and ``//mxpack add [id]``.
* Feature: Add a setting to decide how many days a map should be classified as 'new' and be included in the mapfolder 'new maps'.
* Feature: Added a warn button to the manage players view (``//players``).
* Feature: Add a timeout to the chatvotes, the timeout is an adjustable setting. (default 120 seconds).

* Improvement: The dedimania welcome message also contains the limits of the player and server according to their donation status. (This is a setting and can be turned on, off by default!)
* Improvement: Small improvements in the map karma app related to usability and chat feedback.



0.6.4 (17 February 2019)
------------------------

Core
~~~~

* Improvement: Upgrade several external libraries.
* Improvement: Fix English grammar mistake.

* Security: Make sure that the Yaml files are loaded with the safe method.

* Bugfix: Fixing the integer overflow when extending the time limit too much (for TA modes).
* Bugfix: Make sure to await the coroutine in the royal points callback.

Apps
~~~~

* Improvement: Make sure the user can use the localcps and dedicps when not having an record (just to view the checkpoint times).


0.6.3 (17 November 2018)
------------------------

Core
~~~~

* Bugfix: Fixing loading of settings on some setups.


0.6.2 (17 November 2018)
------------------------

Core
~~~~

* Security: Upgraded library to solve security issues (requests library).

* Bugfix: Fixing issues with the command line interface and showing settings error, preventing executing commands outside project

Apps
~~~~

* Bugfix: Fix issue with clearing the jukebox and locking up the whole jukebox app.


0.6.1 (7 October 2018)
----------------------

Core
~~~~

* Improvement: Added compatibility with Python 3.7.x.
* Improvement: Upgraded external libraries.
* Improvement: Giant performance improvement when indexing maps, karma and local-records data after writing maplist and booting for large servers.

* Bugfix: Fixing issue with invalid JSON files (settings). Will show a correct error message.
* Bugfix: Fixing readmaplist.

Apps
~~~~

* Bugfix: Fix issue in Local Records. Trying to initiate widget before the widget is created in the context.
* Bugfix: Fixing incorrect differences on the live cp times (live rankings) in laps mode.
* Bugfix: Fixing issues with Dedimania in Laps mode.
* Bugfix: Fixing issues with cleaning the Dedimania replays.
* Bugfix: Fixing issue with Dedimania and first driven record (global while it should be only to the person).
* Bugfix: Fixing issue with recording of normal and expanded karma scores in karma app.


0.6.0 (5 May 2018)
------------------

Core
~~~~

* **Breaking**: Removed the deprecated ``app.ui``.

* Feature: Add in-game and command line upgrade commands (//upgrade and ./manage.py upgrade) (CAUTION: Can be unstable!).

* Improvement: Slightly improved the performance when booting PyPlanet on large servers (indexing of local and karma)
* Improvement: Increased the retry count for connecting to a dedicated server from 5 to 10 retries.
* Improvement: Added bumpversion to project (technical and only for development).
* Improvement: Unpack the flags of the ``PlayerInfoChange`` callback and expand the flow variables (technical).
* Improvement: Updated external libraries.
* Improvement: Extract the zone information for players (technical).
* Improvement: Add nation to join and leave messages.
* Improvement: Activated the shutdown handlers to safely exit PyPlanet. The stop callbacks are now called at shutdown of PyPlanet.
* Improvement: Show pre-release as update when running on a pre-release version. (We now release pre-releases for public testing).

* Bugfix: Fix issue when trying to //reboot on Windows.

Apps
~~~~

* NEW: Add Music Server App: Queue music on your server. Add ``pyplanet.apps.contrib.music_server`` to your apps.py.
       More information: http://www.pypla.net/en/latest/apps/contrib/music_server.html

* NEW: Add Advertisement App: Show Discord and PayPal logos in-game. Add ``pyplanet.apps.contrib.ads`` to your apps.py.
       More information: http://www.pypla.net/en/latest/apps/contrib/ads.html

* NEW: Add Queue App: Add a queue for your spectators to fairly join on busy servers. Add ``pyplanet.apps.contrib.queue`` to your apps.py.
       More information: http://www.pypla.net/en/latest/apps/contrib/queue.html

* Feature: Add settings to change vote ratio for the chat voting app.
* Feature: Add advanced voting (++, +, +-, -, --).
* Feature: Add MX Karma integration. You can configure this in-game with //settings and retrieve a key from: https://karma.mania-exchange.com/
* Feature: Add Admin Toolbar to manage your server a bit faster. (you can disable this in //settings)
* Feature: Add new vote to extend the time limit on TA modes (better than /replay or /restart, try it!).
* Feature: Add admin command to extend the time limit on TA modes temporary (//extend [time to extend with] or empty for double the current limit).
* Feature: Add dedimania checkpoint comparison (/dedicps and /dedicps [record number]) to compare your checkpoint times with the record given (or first when none given).
* Feature: Add local record checkpoint comparison (/localcps and /localcps [record number]) to compare your checkpoint times with the record given (or first when none given).
* Feature: Add F7 to hide most of the widgets (concentration mode).
* Feature: Add /topsums statistics to see the top local record players.
* Feature: Add buttons to delete local records by an admin.
* Feature: Add checkpoint difference in the middle of the screen when passing checkpoints (in the sector_times app).
* Feature: Cleanup the dedimania ghost files after reading and sending to dedimania API.
* Feature: Add advanced /list for searching and sorting with your personal local record, the time difference and karma. (can take long on big servers).

* Improvement: Add caching to the /list view per player and per view.

* Bugfix: Fix issue with incorrect link in the dedimania settings entry.
* Bugfix: Fix the type inconsistency of the dedimania API and driven records
* Bugfix: Fix when trying to vote after restarting the map in the podium sequence.
* Bugfix: Fix the retry logic of Dedimania when losing connection.


0.5.4
-----

Core
~~~~

* Improvement: Add unit testing on Windows platform (Technically, using AppVeyor).

* Bugfix: Make sure script names with folders are cleaned and stripped from folder names in most cases.

Apps
~~~~

* Feature: Add button and window to change a folder's name.

* Improvement: Juke maps that are just added the correct order.
* Improvement: Allow the best CP widget for all modes.
* Improvement: Add blacklist write and read commands, now writes when adding player to blacklist and reads when PyPlanet starts.

* Bugfix: Fix the scoreprogression command and window.
* Bugfix: Fix issue when map list was saved to disk and all auto-folders where empty afterwards.
* Bugfix: Fix issue where the dedimania records where not reloaded when game mode changed and map has been restarted.
* Bugfix: Fix message when 2 players rapidly vote and the vote has passed.


0.5.3
-----

Apps
~~~~

* Bugfix: Fixing issue with spamming chat vote reminder.
* Bugfix: Fixing admin pass message when forcing pass a vote.


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
