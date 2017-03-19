import asyncio
import logging

from pyplanet.apps import Apps
from pyplanet.conf import settings
from pyplanet.core import events
from pyplanet.core.db.database import Database
from pyplanet.core.gbx import GbxClient, register_gbx_callbacks
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
		self.loop = 			asyncio.new_event_loop()

		self.gbx = 				GbxClient.create_from_settings(settings.DEDICATED[self.process_name])
		self.db = 				Database.create_from_settings(settings.DATABASES[self.process_name])
		self.signal_manager = 	events.Manager
		self.apps = 			Apps(instance=self)

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

		# Let the gbx.listen run in separate thread. TODO: Not anymore, should look into this again asap!.
		# self.gbx.thread.start()
		register_gbx_callbacks()

		# Initiate the database connection.
		self.db.connect()

		# Initiate apps assets and models.
		self.apps.discover()

		# Execute migrations and initial tasks.
		self.db.initiate()

		# Start the apps, call the on_ready, resulting in apps user logic to be started.
		self.apps.start()

		# Start processing the gbx queue.
		self.gbx.listen()
