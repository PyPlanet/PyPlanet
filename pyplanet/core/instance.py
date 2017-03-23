import asyncio
import logging

from pyplanet import __version__ as version
from pyplanet.apps import Apps
from pyplanet.conf import settings
from pyplanet.core.events import SignalManager
from pyplanet.core.db.database import Database
from pyplanet.core.game import Game
from pyplanet.core.gbx import GbxClient
from pyplanet.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class Instance:
	def __init__(self, process_name):
		"""
		The actual instance of the controller.
		:param process_name: EnvironmentProcess class specific for this process.
		:type process_name: str
		"""
		self.process_name = 	process_name
		self.loop = 			asyncio.get_event_loop()
		self.game =				Game

		self.gbx = 				GbxClient.create_from_settings(self, settings.DEDICATED[self.process_name])
		self.db = 				Database.create_from_settings(self, settings.DATABASES[self.process_name])
		self.signal_manager = 	SignalManager
		self.apps = 			Apps(self)

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

	async def __start(self):
		"""
		The start coroutine is executed when the process is ready to create connection to the gbx protocol, database,
		other services and finally start the apps.
		"""
		# Make sure we start the Gbx connection, authenticate, set api version and stuff.
		await self.gbx.connect()

		# Initiate the database connection.
		self.db.connect()

		# Initiate apps assets and models.
		self.apps.discover()

		# Execute migrations and initial tasks.
		self.db.initiate()

		# Start the apps, call the on_ready, resulting in apps user logic to be started.
		self.apps.start()
		# await self.gbx.execute('ChatSendServerMessage', '$o$w$FD4Py$369Planet$g v{}'.format(version)),

		# Finish signalling and send finish signal.
		await self.signal_manager.finish_start()
