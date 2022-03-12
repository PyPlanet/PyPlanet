"""
Settings for the PyPlanet application.

Values will dynamically read from the env-vars provided by your setup. All default values will be overwritten.
Default values are retrieved from `default_settings.py`.
"""
import os

from pyplanet.conf import default_settings


class LazySettings:
	"""
	THe lazy settings class will cache and merge settings form environment variables. It mixes in the default values.
	"""

	def __init__(self):
		self._settings = dict()

	def __getattr__(self, item):
		"""
		Get value from local or env settings.
		"""
		if item in self._settings:
			return self._settings[item]
		if os.getenv(item):
			if item in ['PYPLANET_APPS', 'PYPLANET_MANDATORY_APPS']:
				return os.getenv(item).split(' ')
			return os.getenv(item)
		if hasattr(default_settings, item):
			return getattr(default_settings, item)
		return None

	def __setattr__(self, key, value):
		"""
		Set and clear cached settings.
		"""
		if key != '_settings':
			self._settings[key] = value
		else:
			super().__setattr__(key, value)

	def __delattr__(self, item):
		"""
		Delete cached settings.
		"""
		super().__delattr__(item)
		self._settings.pop(item, None)


settings = LazySettings()
