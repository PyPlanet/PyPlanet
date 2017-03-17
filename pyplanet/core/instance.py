import logging

from pyplanet.apps import Apps
from pyplanet.conf import settings
from pyplanet.core import events
from pyplanet.core.db.database import Database
from pyplanet.core.gbx import GbxClient
from pyplanet.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class Instance:
	def __init__(self, process):
		"""
		The actual instance of the controller.
		:param process: EnvironmentProcess class specific for this process.
		:type process: pyplanet.god.process.EnvironmentProcess
		"""
		self.process = 			process
		self.loop = 			self.process.loop

		self.gbx = 				GbxClient.create_from_settings(settings.DEDICATED[self.process.name])
		self.db = 				Database.create_from_settings(settings.DATABASES[self.process.name])
		self.signal_manager = 	events.Manager
		self.apps = 			Apps(instance=self)

		# Populate apps.
		self.apps.populate(settings.MANDATORY_APPS, in_order=True)
		try:
			self.apps.populate(settings.APPS[self.process.name])
		except KeyError as e:
			raise ImproperlyConfigured(
				'One of the pool names doesn\'t reflect intot the APPS setting! You must '
				'declare the apps per pool! ({})'.format(str(e))
			)

	async def start(self):
		"""
		The start coroutine is executed when the process is ready to create connection to the gbx protocol, database,
		other services and finally start the apps.
		"""
		# Make sure we start the Gbx connection, authenticate, set api version and stuff.
		await self.gbx.connect()

		# Let the gbx.listen run in separate thread.
		self.gbx.thread.start()

		# Initiate the database connection.
		self.db.connect()

		# Initiate apps assets and models.
		self.apps.discover()

		# Execute migrations and initial tasks.
		self.db.initiate()

		# Start the apps, call the on_ready, resulting in apps user logic to be started.
		self.apps.start()
