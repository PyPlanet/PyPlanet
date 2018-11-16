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
		self.module = os.environ.get('PYPLANET_SETTINGS_MODULE')

		if not self.module:
			raise ImproperlyConfigured(
				'Settings module is not defined! Please define PYPLANET_SETTINGS_MODULE in your environment or start script.'
			)

		# Add the module itself to the configuration.
		self.settings['SETTINGS_MODULE'] = self.module

		# Load the module, put the settings into the local context.
		module = importlib.import_module(self.module)

		for setting in dir(module):
			if setting.isupper():
				self.settings[setting] = getattr(module, setting)
