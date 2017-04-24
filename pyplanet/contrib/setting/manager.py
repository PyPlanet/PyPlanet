import asyncio


class _BaseSettingManager:
	"""
	Setting  Manager.
	Todo: Write introduction.
	"""
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance
		self._settings = list()
		self._app = None

	async def initiate_setting(self, setting):
		"""
		Initiate setting, make sure we have a database record filled with empty (null) value.
		
		:param setting: Setting instance.
		:type setting: pyplanet.contrib.setting.setting._Setting
		"""
		# TODO.
		pass

	async def register(self, *settings):
		"""
		Register your setting(s). This will create default values when the setting has not yet been inited before.

		:param settings: Setting(s) given.
		:type settings: pyplanet.contrib.setting.setting._Setting
		"""
		# Check if setting has a value, then fetch it, if not, create new entry with default or none.
		await asyncio.gather(*[self.initiate_setting(s) for s in settings])

		# Register the setting.
		self._settings.extend(settings)


class GlobalSettingManager(_BaseSettingManager):
	def __init__(self, instance):
		super().__init__(instance)
		self.app_managers = dict()

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


class AppSettingManager(_BaseSettingManager):
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
		await asyncio.gather(*[self.initiate_setting(s) for s in settings])

		# Register the setting.
		self._settings.extend(settings)
