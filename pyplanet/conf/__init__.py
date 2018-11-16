"""
Settings for the PyPlanet application.

Values will dynamically read from the settings module provided by your setup. All default values will be overwritten.
Default values are retrieved from `default_settings.py`.
"""
import logging
import os

from pyplanet.conf import default_settings
from pyplanet.conf.backends.json import JsonConfigBackend
from pyplanet.conf.backends.python import PythonConfigBackend
from pyplanet.conf.backends.yaml import YamlConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured


class LazySettings:
	"""
	THe lazy settings class will cache and merge settings that the settings module provided and the defaults
	of the system.
	"""
	BACKEND = {
		'python': PythonConfigBackend,
		'json': JsonConfigBackend,
		'yaml': YamlConfigBackend,
	}

	def __init__(self):
		self._settings = None

	def _setup(self, optional_loading=False):
		"""
		Setup will create the wrapped settings and load the settings module.
		"""
		settings_method = os.environ.get('PYPLANET_SETTINGS_METHOD', 'python')
		if not settings_method and not optional_loading:
			raise ImproperlyConfigured(
				'Settings method is not defined! Please define PYPLANET_SETTINGS_METHOD in your '
				'environment or start script. The possible values: \'python\', \'json\', \'yaml\''
			)

		self._settings_method = settings_method
		try:
			self._settings_method_class = self.BACKEND[settings_method]
		except:
			raise ImproperlyConfigured(
				'The provided settings method \'{}\' does not exist in the current PyPlanet version!'
				'The current possible methods: \'python\', \'json\', \'yaml\'.'
			)

		# Initiate the backend class.
		self._settings = self._settings_method_class()

		# Load the contents.
		try:
			self._settings.load()
		except Exception as e:
			if not optional_loading:
				logging.exception(e)
				exit(1)

	def __getattr__(self, item):
		"""
		Get value from local or wrapped settings.
		"""
		if self._settings is None:
			self._setup()
		val = self._settings.get(item)
		self.__dict__[item] = val
		return val

	def __setattr__(self, key, value):
		"""
		Set and clear cached settings.
		"""
		if key == '_settings':
			self.__dict__.clear()
		else:
			self.__dict__.pop(key, None)
		super().__setattr__(key, value)

	def __delattr__(self, item):
		"""
		Delete cached settings.
		"""
		super().__delattr__(item)
		self.__dict__.pop(item, None)

	@property
	def configured(self):
		"""
		Return True if the settings have already been configured.
		"""
		return self._settings is not None

	def reset(self):
		"""
		Clear the current wrapped settings. Useful when reloaded or in tests.
		"""
		self._settings = None


settings = LazySettings()
