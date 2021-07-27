import os

from pyplanet.conf.backends.base import ConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured


class EnvironmentConfigBackend(ConfigBackend):
	name = 'env'

	def __init__(self, **options):
		super().__init__(**options)

		self.module = None

	def load(self):
		# Make sure we load the defaults first.
		super().load()

		# Check if env file should be loaded from specific path.
		env_file = None
		if 'PYPLANET_ENV_PATH' in os.environ:
			# TODO: envfile load from this file.
			pass
		else:
			# TODO: Detect envfile in work dir.
			pass

		# Load env file found/given.
		if env_file:
			# TODO: Load env file.
			pass

		# Verify required env variables.
		# TODO: Verify required variables.


		# Load from the modules.
		processed = 0
		for setting in dir(module):
			if setting.isupper():
				self.settings[setting] = getattr(module, setting)
				processed += 1

		# Check for empty results.
		if processed < 1:
			raise ImproperlyConfigured(
				'The settings module doesn\'t contain any submodules or files to load! Please make sure '
				'your settings module exist or contains the files base.py and apps.py. Your module: {}'.format(self.module)
			)
