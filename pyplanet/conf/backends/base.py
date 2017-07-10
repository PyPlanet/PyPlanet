from pyplanet.conf import default_settings

_GLOBAL_DEFAULT = object()


class ConfigBackend:
	"""
	The base config backend class contains everything in place for one-time loading and memory pooled configuration.
	You only have to override the name property and the ``load()`` method to have a file reader working.

	Please make sure you convert all keys to UPPER in your ``load()`` before you store it in ``self.settings``!

	"""
	name = None

	def __init__(self, **options):
		self.options = options
		self.defaults = dict()
		self.settings = dict()
		self.settings['SETTINGS_METHOD'] = self.name

	def load(self):
		"""
		Load method. Override this method and call the ``super().load()`` to load defaults before you load your configuration
		file or backend.
		"""
		# Add default configuration to our cached/static context.
		for setting in dir(default_settings):
			if setting.isupper():
				self.defaults[setting] = getattr(default_settings, setting)

	def is_overriden(self, setting):
		"""
		Is the setting overriden by local settings module?

		:param setting: setting to check
		:type setting: str
		:return: boolean
		:rtype: bool
		"""
		return setting.upper() in self.settings

	def get(self, key, default=_GLOBAL_DEFAULT):
		"""
		Get a setting by key, return the value or if not exists the default parameter given or if the default parameter
		is not given the provided default in the PyPlanet version.

		:param key: Key of setting, case sensitive! All keys are in uppercase!
		:param default: Default override. Leave empty/don't provide to use the defaults by PyPlanet.
		:type key: str
		:return: Value of setting.
		"""
		if key in self.settings:
			return self.settings[key]
		if default != _GLOBAL_DEFAULT:
			return default
		if key in self.defaults:
			return self.defaults[key]
		raise KeyError(key)

	def set(self, key, value):
		"""
		Set a setting by key and set the provided value. Please keep in mind that not all configuration backends
		support setting values!

		:param key: Key of setting, case sensitive! All keys are in uppercase!
		:param value: Value to set.
		:raise: NotImplementedError
		"""
		raise NotImplementedError('Settings can not be written with this backend!')
