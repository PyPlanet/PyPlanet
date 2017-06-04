import threading

import logging

from pyplanet.conf import settings
from pyplanet.core.management import BaseCommand
from pyplanet.god.pool import EnvironmentPool
from pyplanet.utils.log import initiate_logger


class Command(BaseCommand):
	help = 'Start the PyPlanet god with all it\'s subprocesses.'

	requires_system_checks = False
	requires_migrations_checks = False

	def add_arguments(self, parser):
		parser.add_argument('--max-restarts', type=int, default=0)
		parser.add_argument('--tokio', dest='tokio', action='store_true')

	def handle(self, *args, **options):
		# Initiate the logger.
		threading.current_thread().setName('Main')
		initiate_logger()
		logger = logging.getLogger(__name__)

		# Initiate the settings by accessing one.
		logger.debug('Initiated configuration and environment... (debug on, means no error reporting and verbose output')
		if not settings.DEBUG:
			logger.info('Initiated configuration and environment...')
		logger.info('-------------------------------[  PyPlanet v{}  ]-------------------------------'.format(self.get_version()))

		# Start god process (the current started process).
		pool = EnvironmentPool(settings.POOLS, max_restarts=options['max_restarts'], options=options)
		pool.populate()

		# Starting all processes.
		pool.start()

		# Start the watchdog.
		try:
			pool.watchdog()
		except KeyboardInterrupt:
			pool.shutdown()
			exit(0)
