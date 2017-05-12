import asyncio

from pyplanet.apps import AppConfig
from pyplanet.contrib import CoreContrib
from pyplanet.contrib.setting.core_settings import performance_mode
from pyplanet.contrib.setting.exceptions import SettingException


class _BaseSettingManager:
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance
		self._settings = list()
		self._app = None

	async def register(self, *settings):
		"""
		Register your setting(s). This will create default values when the setting has not yet been inited before.

		:param settings: Setting(s) given.
		:type settings: pyplanet.contrib.setting.setting._Setting
		"""
		# Check if setting has a value, then fetch it, if not, create new entry with default or none.
		await asyncio.gather(*[s.initiate_setting() for s in settings])

		# Register the setting.
		self._settings.extend(settings)


class GlobalSettingManager(_BaseSettingManager, CoreContrib):
	"""
	Global Setting manager is available at the instance. ``instance.setting_manager``.
	
	.. warning::
	
		Don't use the setting_manager for registering app settings! Use the app setting manager instead!
		
		Don't initiate this class yourself.
	
	"""

	def __init__(self, instance):
		super().__init__(instance)
		self.app_managers = dict()

	async def on_start(self):
		# Register core global settings.
		await self.register(performance_mode)

	def create_app_manager(self, app_config):
		"""
		Create app setting manager.
		
		:param app_config: App Config instance.
		:type app_config: pyplanet.apps.config.AppConfig
		:return: Setting Manager
		:rtype: pyplanet.contrib.setting.manager.AppSettingManager
		"""
		if app_config.label not in self.app_managers:
			self.app_managers[app_config.label] = AppSettingManager(self._instance, app_config)
		return self.app_managers[app_config.label]

	def get_app_manager(self, app):
		"""
		Get the app manager for a specified app label or config instance.
		
		:param app: App label in string or the app config instance.
		:return: App manager instance.
		:rtype: pyplanet.contrib.setting.manager.AppSettingManager
		"""
		if isinstance(app, AppConfig):
			app = app.label
		return self.app_managers[app]

	@property
	def recursive_settings(self):
		"""
		Retrieve all settings, of all submanagers.
		"""
		for setting in self._settings:
			yield setting
		for app, manager in self.app_managers.items():
			for setting in manager._settings:
				yield setting

	async def get_setting(self, app_label, key, prefetch_values=True):
		"""
		Get setting by key and optionally fetch the value if not yet fetched.

		:param app_label: Namespace (mostly app label).
		:param key: Key string
		:param prefetch_values: Prefetch the values if not yet fetched?
		:return: Setting instance.
		:raise: SettingException
		"""
		if app_label is None:
			setting = None
			for s in self._settings:
				if s.key == key:
					setting = s
					break

			if not setting:
				raise SettingException('Setting with key not found')

			if prefetch_values and setting._value[0] is False:
				await setting.get_value()
			return setting
		return await self.get_app_manager(app_label).get_setting(key, prefetch_values)

	async def get_apps(self, prefetch_values=True):
		"""
		Get all the app label + names for all the settings we can find in our registry.
		Returns a dict with label as key, and count + name as values.
		
		:param prefetch_values: Prefetch the values in this call. Defaults to True.
		:return: List with setting objects.
		"""
		apps = dict()
		if prefetch_values:
			await asyncio.gather(*[
				s.get_value(refresh=True) for s in self.recursive_settings
			])

		for setting in self.recursive_settings:
			if setting.app_label not in apps:
				apps[setting.app_label] = dict(
					count=0,
					name=self._instance.apps.apps[setting.app_label].name,
					app=self._instance.apps.apps[setting.app_label],
					settings=list()
				)
			apps[setting.app_label]['count'] += 1
			apps[setting.app_label]['settings'].append(setting)
		return apps

	async def get_categories(self, prefetch_values=True):
		"""
		Get all the categories we have registered.
		Returns a dict with label as key, and count + name as values.
		
		:param prefetch_values: Prefetch the values in this call. Defaults to True.
		:return: List with setting objects.
		"""
		cats = dict()
		if prefetch_values:
			await asyncio.gather(*[
				s.get_value(refresh=True) for s in self.recursive_settings
			])

		for setting in self.recursive_settings:
			if setting.category not in cats:
				cats[setting.category] = dict(
					count=0,
					name=setting.category,
					settings=list()
				)
			cats[setting.category]['count'] += 1
			cats[setting.category]['settings'].append(setting)
		return cats

	async def get_all(self, prefetch_values=True):
		"""
		Retrieve a list of settings, with prefetched values, so get_value is almost instant (or use ._value, not recommended).
		
		:param prefetch_values: Prefetch the values in this call. Defaults to True.
		:return: List with setting objects.
		"""
		if prefetch_values:
			await asyncio.gather(*[
				s.get_value(refresh=True) for s in self.recursive_settings
			])
		return self.recursive_settings


class AppSettingManager(_BaseSettingManager):
	"""
	The local app setting manager is the one you should use to register settings to inside of your app.
	
	You can use this manager like this:
	
	.. code-block:: python

		from pyplanet.contrib.setting import Setting	
	
		async def on_start(self):
			await self.context.setting.register(
				Setting('feature_a', 'Enable feature A', Setting.CAT_FEATURES, type=bool, description='Enable feature A'),
				Setting('feature_b', 'Enable feature B', Setting.CAT_FEATURES, type=bool, description='Enable feature B'),
			)
			
	For more information about the settings, categories, types, and all other options. Look at the ``Settings`` 
	documentation.
	
	.. warning::
	
		Don't initiate this class yourself.
	
	"""

	def __init__(self, instance, app):
		"""
		Initiate app setting manager.
		
		:param instance: Controller instance.
		:param app: App Config instance.
		:type instance: pyplanet.core.instance.Instance
		:type app: pyplanet.apps.config.AppConfig
		"""
		super().__init__(instance)
		self._app = app

	async def register(self, *settings):
		"""
		Register your setting(s). This will create default values when the setting has not yet been inited before.

		:param settings: Setting(s) given.
		:type settings: pyplanet.contrib.setting.setting._Setting
		"""
		# Set app label on all setting objects.
		for setting in settings:
			setting.app_label = self._app.label

		# Check if setting has a value, then fetch it, if not, create new entry with default or none.
		await asyncio.gather(*[s.initiate_setting() for s in settings])

		# Register the setting.
		self._settings.extend(settings)

	async def get_setting(self, key, prefetch_values=True):
		"""
		Get setting by key and optionally fetch the value if not yet fetched.

		:param key: Key string
		:param prefetch_values: Prefetch the values if not yet fetched?
		:return: Setting instance.
		:raise: SettingException
		"""
		setting = None
		for s in self._settings:
			if s.key == key:
				setting = s
				break

		if not setting:
			raise SettingException('Setting with key not found')

		if prefetch_values and setting._value[0] is False:
			await setting.get_value()
		return setting

	def get_categories(self):
		"""
		Get all the categories we have registered.
		Returns a dict with label as key, and count + name as values.
		"""
		cats = dict()
		for setting in self._settings:
			if setting.category not in cats:
				cats[setting.category] = dict(count=0)
			cats[setting.category]['count'] += 1
		return cats

	async def get_all(self, prefetch_values=True):
		"""
		Retrieve a list of settings, with prefetched values, so get_value is almost instant (or use ._value, not recommended).
		
		:param prefetch_values: Prefetch the values in this call. Defaults to True.
		:return: List with setting objects.
		"""
		if prefetch_values:
			await asyncio.gather(*[
				s.get_value(refresh=True) for s in self._settings
			])
		return self._settings

