import importlib
import os

from pyplanet.conf.backends.base import ConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured


class PythonConfigBackend(ConfigBackend):
	name = 'python'

	def __init__(self, **options):
		super().__init__(**options)

		self.module = None

	def load(self):
		# Make sure we load the defaults first.
		super().load()

		# Prepare the loading.
		self.module = os.environ.get('PYPLANET_SETTINGS_MODULE', 'settings')

		if not self.module:
			raise ImproperlyConfigured(
				'Settings module is not defined! Please define PYPLANET_SETTINGS_MODULE in your environment or start script.'
			)

		# Add the module itself to the configuration.
		self.settings['SETTINGS_MODULE'] = self.module

		# Load the module, put the settings into the local context.
		try:
			module = importlib.import_module(self.module)
		except ModuleNotFoundError as e:
			raise ImproperlyConfigured(
				'The settings module doesn\'t contain any submodules or files to load! Please make sure '
				'your settings module exist or contains the files base.py and apps.py. Your module: {}'.format(self.module)
			) from e

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
