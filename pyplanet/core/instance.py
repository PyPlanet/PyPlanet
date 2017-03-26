import asyncio
import logging

from pyplanet import __version__ as version

from pyplanet.apps import Apps
from pyplanet.conf import settings
from pyplanet.contrib.permission import PermissionManager
from pyplanet.core import signals
from pyplanet.core.events import SignalManager
from pyplanet.core.db.database import Database
from pyplanet.core.game import Game
from pyplanet.core.gbx import GbxClient
from pyplanet.core.exceptions import ImproperlyConfigured

from pyplanet.contrib.map import MapManager
from pyplanet.contrib.player import PlayerManager

logger = logging.getLogger(__name__)


class Instance:
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
		self.signal_manager = 		SignalManager
		self.apps = 				Apps(self)

		# Contrib components.
		self.map_manager =			MapManager(self)
		self.player_manager =		PlayerManager(self)
		self.permission_manager =	PermissionManager(self)

		# Populate apps.
		self.apps.populate(settings.MANDATORY_APPS, in_order=True)
		try:
			self.apps.populate(settings.APPS[self.process_name])
		except KeyError as e:
			raise ImproperlyConfigured(
				'One of the pool names doesn\'t reflect intot the APPS setting! You must '
				'declare the apps per pool! ({})'.format(str(e))
			)

	def start(self):
		"""
		Start wrapper.
		"""
		self.loop.run_until_complete(self.__start())
		self.loop.run_forever()

	async def __fire_signal(self, signal):
		"""
		Fire signal with given name to all listeners.
		:param signal: Signal to fire on.
		:type signal: pyplanet.core.events.dispatcher.Signal
		"""
		await signal.send(dict(instance=self))

	async def __start(self):
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
		await self.db.connect()		# Connect and initial state.
		await self.apps.discover() 	# Discover apps models.
		await self.db.initiate() 	# Execute migrations and initial tasks.
		await self.apps.init()
		await self.__fire_signal(signals.pyplanet_start_db_after)

		# Start the apps, call the on_ready, resulting in apps user logic to be started.
		await self.print_header()
		await self.__fire_signal(signals.pyplanet_start_apps_before)
		await self.apps.start()
		await self.__fire_signal(signals.pyplanet_start_apps_after)
		await self.print_footer()

		# Finish signalling and send finish signal.
		await self.signal_manager.finish_start()
		await self.__fire_signal(signals.pyplanet_start_after)

	async def print_header(self):
		pass
		await self.gbx.execute('ChatSendServerMessage', '$n$fff--------------------------------------------------------------------')
		await self.gbx.execute('ChatSendServerMessage', '$o$FD4Py$369Planet$z$fff Starting (v{}) ...'.format(version))

	async def print_footer(self):
		pass
		await self.gbx.execute('ChatSendServerMessage', '$fff    Successfully started {} apps.'.format(len(self.apps.apps)))
		await self.gbx.execute('ChatSendServerMessage', '$n$fff--------------------------------------------------------------------')


class _Controller:
	def __init__(self, *args, **kwargs):
		self.name = None
		self.__instance = None

	def prepare(self, name):
		self.name = name
		self.__instance = Instance(name)
		return self

	@property
	def instance(self):
		"""
		Get active instance in current process.
		:return: Controller Instance
		:rtype: pyplanet.core.instance.Instance
		"""
		return self.__instance

Controller = _Controller()
