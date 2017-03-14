import argparse
import sys

import logging.config

from pyplanet.conf import settings
from pyplanet.utils.log import initiate_logger
from pyplanet.god.pool import EnvironmentPool


class Management:
	def __init__(self, argv=None):
		self.argv = argv or sys.argv
		self.parser = argparse.ArgumentParser(prog=self.argv.pop(0))
		self.arguments = object()
		self.logger = logging.getLogger(__name__)
		self.add_arguments()

	def add_arguments(self):
		self.parser.add_argument('--settings')
		# TODO.

	def execute(self):
		# Parse arguments.
		self.arguments = self.parser.parse_args(self.argv)

		# Initiate the logger.
		initiate_logger()
		self.logger = logging.getLogger(__name__)

		# Initiate the settings by accessing one.
		self.logger.info('Initiating settings...')
		if settings.DEBUG:
			self.logger.debug('Running in debug mode, will not report any errors and show verbose output!')

		# Start god process (the current started process).
		pool = EnvironmentPool(settings.POOLS)
		pool.populate()

		# Starting all processes.
		pool.start()


def start(argv=None):
	"""
	Run the utility from CLI.
	:param argv: arguments.
	"""
	utility = Management(argv)
	utility.execute()
