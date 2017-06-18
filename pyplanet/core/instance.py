import asyncio
import logging

from pyplanet.utils.analytics import Analytics
from .controller import Controller as _Controller

from pyplanet import __version__ as version

from pyplanet.apps import Apps
from pyplanet.conf import settings
from pyplanet.core import signals
from pyplanet.core.events import SignalManager
from pyplanet.core.db.database import Database
from pyplanet.core.game import Game
from pyplanet.core.gbx import GbxClient
from pyplanet.core.exceptions import ImproperlyConfigured
from pyplanet.core.storage.storage import Storage
from pyplanet.core.ui import GlobalUIManager
from pyplanet.utils import memleak, releases

from pyplanet.contrib.map import MapManager
from pyplanet.contrib.player import PlayerManager
from pyplanet.contrib.command import CommandManager
from pyplanet.contrib.permission import PermissionManager
from pyplanet.contrib.setting import GlobalSettingManager
from pyplanet.contrib.mode import ModeManager
from pyplanet.contrib.chat import ChatManager

logger = logging.getLogger(__name__)


class Instance:
	"""
	Controller Instance. The very base of the controller, containing class instances of all core components.

	:ivar process_name: Process and pool name.
	:ivar loop: AsyncIO Event Loop.
	:ivar game: Game Information class.
	:ivar apps: Apps component.
	:ivar gbx: Gbx component.
	:ivar db: Database component.
	:ivar storage: Storage component.
	:ivar signal_manager: Signal Manager.
	:ivar ui_manager: UI Manager (global). Please use the APP context UI manager instead!

	:ivar map_manager: Contrib: Map Manager.
	:ivar player_manager: Contrib: Player Manager.
	:ivar permission_manager: Contrib: Permission Manager.
	:ivar command_manager: Contrib: Command Manager.
	:ivar setting_manager: Contrib: Setting Manager. Please use the APP context setting manager instead!
	:ivar mode_manager: Contrib. Mode Manager.
	"""

	def __init__(self, process_name):
		"""
		The actual instance of the controller.

		:param process_name: EnvironmentProcess class specific for this process.
		:type process_name: str
		"""
		# Initiate all the core components.
		self.process_name = 		process_name
		self.loop = 				asyncio.get_event_loop()
		self.game =					Game

		self.gbx = 					GbxClient.create_from_settings(self, settings.DEDICATED[self.process_name])
		self.db = 					Database.create_from_settings(self, settings.DATABASES[self.process_name])
		self.storage =				Storage.create_from_settings(self, settings.STORAGE[self.process_name])
		self.signal_manager = 		SignalManager
		self.ui_manager =			GlobalUIManager(self)
		self.apps = 				Apps(self)

		# Contrib components.
		self.map_manager =				MapManager(self)
		self.player_manager =			PlayerManager(self)
		self.permission_manager =		PermissionManager(self)
		self.command_manager =			CommandManager(self)
		self.setting_manager =			GlobalSettingManager(self)
		self.mode_manager =				ModeManager(self)
		self.chat_manager = self.chat = ChatManager(self)

		# Populate apps.
		self.apps.populate(settings.MANDATORY_APPS, in_order=True)
		try:
			self.apps.populate(settings.APPS[self.process_name])
		except KeyError as e:
			raise ImproperlyConfigured(
				'One of the pool names doesn\'t reflect into the APPS setting! You must '
				'declare the apps per pool! ({})'.format(str(e))
			)

	def start(self, run_forever=True):  # pragma: no cover
		"""
		Start wrapper.
		"""
		try:
			# Start memleak checker.
			memleak.checker.start()

			# Initiate instance
			self.loop.run_until_complete(self._start())

			# Run forever.
			if run_forever:
				self.loop.run_forever()
		except KeyboardInterrupt:
			pass
		except Exception as e:
			logger.exception(e)
			raise

	@property
	def performance_mode(self):
		"""
		Gives back a boolean, True if we are in performance mode.

		:return: Performance mode boolean.
		"""
		return self.player_manager.performance_mode

	async def __fire_signal(self, signal):  # pragma: no cover
		"""
		Fire signal with given name to all listeners.

		:param signal: Signal to fire on.
		:type signal: pyplanet.core.events.dispatcher.Signal
		"""
		await signal.send(dict(instance=self))

	async def _start(self):  # pragma: no cover
		"""
		The start coroutine is executed when the process is ready to create connection to the gbx protocol, database,
		other services and finally start the apps.
		"""
		# Make sure we start the Gbx connection, authenticate, set api version and stuff.
		await self.__fire_signal(signals.pyplanet_start_gbx_before)
		await self.gbx.connect()
		await self.__fire_signal(signals.pyplanet_start_gbx_after)

		# Initiate the database connection, discover apps assets,models etc.
		await self.__fire_signal(signals.pyplanet_start_db_before)
		await self.db.connect()				# Connect and initial state.
		await self.apps.discover() 			# Discover apps models.
		await self.db.initiate() 			# Execute migrations and initial tasks.
		await self.apps.check()     		# Check for incompatible apps and remove them.
		await self.apps.init()				# Initiate apps
		await self.ui_manager.on_start()    # Initiate UI manager.
		await self.__fire_signal(signals.pyplanet_start_db_after)

		# Start the core contribs.
		await self.setting_manager.on_start()
		await self.map_manager.on_start()
		await self.player_manager.on_start()
		await self.permission_manager.on_start()
		await self.command_manager.on_start()
		await self.mode_manager.on_start()
		await self.chat_manager.on_start()

		# Start the apps, call the on_ready, resulting in apps user logic to be started.
		await self.print_header()
		await self.__fire_signal(signals.pyplanet_start_apps_before)
		await self.apps.start()
		await self.__fire_signal(signals.pyplanet_start_apps_after)
		await self.print_footer()

		# Utils.
		await Analytics.start(self)

		# Finish signalling and send finish signal.
		await self.signal_manager.finish_start()
		await self.__fire_signal(signals.pyplanet_start_after)

	async def print_header(self):  # pragma: no cover
		await self.chat.execute(
			self.chat('', raw=True),
			self.chat('$fff$o$w⏳$z$fff Loading...', raw=True)
		)

	async def print_footer(self):  # pragma: no cover
		await self.chat(
			'\uf1e6 $o$FD4Py$369Planet$z$o$s$fff v{}, {}\uf013 $z$s $369|$FD4 '
			'$l[http://pypla.net]Site$l $369|$FD4 '
			'$l[https://github.com/PyPlanet]Github$l $369|$FD4 '
			'$l[http://pypla.net]Docs$l'.format(version, len(self.apps.apps)),
			raw=True
		)

		try:
			asyncio.ensure_future(releases.UpdateChecker.init_checker(self))
		except:
			pass  # Completely ignore errors while checking for the latest version.


Controller = _Controller
"""
Controller access point to prevent circular imports. This is a lazy provided way to get the instance from anywhere!
:type Controller: pyplanet.core.Controller
:type: pyplanet.core.Controller
"""
