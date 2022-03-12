import os
import logging
import dotenv

from pyplanet.conf.backends.base import ConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class EnvironmentConfigBackend(ConfigBackend):
	name = 'env'

	def __init__(self, **options):
		super().__init__(**options)

		self.module = None

	def load(self):
		# Make sure we load the defaults first.
		super().load()

		# Check if env file should be loaded from specific path.
		if os.getenv('PYPLANET_ENV_PATH'):
			if os.path.exists(os.getenv('PYPLANET_ENV_PATH')):
				dotenv.load_dotenv(os.getenv('PYPLANET_ENV_PATH'))
			else:
				logger.error('Can\'t load env path from PYPLANET_ENV_PATH variable.')
				raise ImproperlyConfigured('Can\'t load env-path given in PYPLANET_ENV_PATH.')
		else:
			dotenv.load_dotenv()

		# Verify required env variables.
		# TODO: Verify required variables.
