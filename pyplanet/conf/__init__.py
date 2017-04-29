"""
Settings for the PyPlanet application.

Values will dynamically read from the settings module provided by your setup. All default values will be overwritten.
Default values are retrieved from `default_settings.py`.
"""
import importlib
import os

from pyplanet.conf import default_settings
from pyplanet.core.exceptions import ImproperlyConfigured


class LazySettings:
	"""
	THe lazy settings class will cache and merge settings that the settings module provided and the defaults
	of the system.
	"""
	def __init__(self):
		self._settings = None

	def _setup(self):
		"""Setup will create the wrapped settings and load the settings module."""
		settings_module = os.environ.get('PYPLANET_SETTINGS_MODULE')
		if not settings_module:
			raise ImproperlyConfigured(
				'Settings module is not defined! Please define PYPLANET_SETTINGS_MODULE in your '
				'environment or start script.'
			)

		self._settings = Settings(settings_module)

	def __getattr__(self, item):
		"""Get value from local or wrapped settings."""
		if self._settings is None:
			self._setup()
		val = getattr(self._settings, item)
		self.__dict__[item] = val
		return val

	def __setattr__(self, key, value):
		"""Set and clear cached settings."""
		if key == '_settings':
			self.__dict__.clear()
		else:
			self.__dict__.pop(key, None)
		super().__setattr__(key, value)

	def __delattr__(self, item):
		"""Delete cached settings."""
		super().__delattr__(item)
		self.__dict__.pop(item, None)

	@property
	def configured(self):
		"""Return True if the settings have already been configured."""
		return self._settings is not None

	def reset(self):
		"""Clear the current wrapped settings. Useful when reloaded or in tests."""
		self._settings = None


class Settings:

	def __init__(self, settings_module):
		"""
		Load the settings from the settings_module provided.
		:param settings_module: Module that contains the local settings.
		:type settings_module: str
		"""
		self._custom_settings = set()

		# Add all default configuration to our context.
		for setting in dir(default_settings):
			if setting.isupper():
				setattr(self, setting, getattr(default_settings, setting))

		# Store the settings module in our context.
		self.SETTINGS_MODULE = settings_module

		# Import the module.
		module = importlib.import_module(self.SETTINGS_MODULE)

		for setting in dir(module):
			if setting.isupper():
				setattr(self, setting, getattr(module, setting))
				self._custom_settings.add(setting)

	def is_overriden(self, setting):
		"""
		Is the setting overriden by local settings module?
		:param setting: setting to check
		:type setting: str
		:return: boolean
		:rtype: bool
		"""
		return setting in self._custom_settings


settings = LazySettings()
