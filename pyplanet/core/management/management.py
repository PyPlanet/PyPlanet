import argparse
import logging.config
import threading

from pyplanet.conf import settings
from pyplanet.utils.log import initiate_logger
from pyplanet.god.pool import EnvironmentPool
from pyplanet import __version__ as version


class Management:
	def __init__(self, argv=None):
		self.parser = argparse.ArgumentParser()
		self.arguments = object()
		self.logger = logging.getLogger(__name__)
		self.add_arguments()

	def add_arguments(self):
		self.parser.add_argument('--settings')
		self.parser.add_argument('--max-restarts', type=int, default=0)
		# TODO.

	def execute(self):
		# Parse arguments.
		self.arguments = self.parser.parse_args()

		# Initiate the logger.
		threading.current_thread().setName('Main')
		initiate_logger()
		self.logger = logging.getLogger(__name__)

		# Initiate the settings by accessing one.
		self.logger.debug('Initiated configuration and environment... (debug on, means no error reporting and verbose output')
		if not settings.DEBUG:
			self.logger.info('Initiated configuration and environment...')
		self.logger.info('-------------------------------[  PyPlanet v{}  ]-------------------------------'.format(version))

		# Start god process (the current started process).
		pool = EnvironmentPool(settings.POOLS, max_restarts=self.arguments.max_restarts)
		pool.populate()

		# Starting all processes.
		pool.start()

		# Start the watchdog.
		try:
			pool.watchdog()
		except KeyboardInterrupt:
			pool.shutdown()
			exit(0)


def start(argv=None):
	"""
	Run the utility from CLI.
	:param argv: arguments.
	"""
	utility = Management(argv)
	utility.execute()
