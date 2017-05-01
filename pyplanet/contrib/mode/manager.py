from pyplanet.contrib import CoreContrib


class ModeManager(CoreContrib):
	"""
	Mode Manager manges the script, script settings and the mode UI settings of the current game mode.
	
	.. warning::
	
		Don't initiate this class yourself. Use ``instance.mode_manager`` for an static instance.

	"""
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		self._current_script = None

	async def on_start(self):
		"""
		Handle startup, just before the apps will start. We will make sure we are ready to get requests for permissions.
		"""
		self._current_script = await self.get_script_name()

	async def get_script_name(self, refresh=False):
		"""
		Get the current script name.
		"""
		if refresh or not self._current_script:
			self._current_script = await self._instance.gbx.execute('GetScriptName')
		return self._current_script

	async def get_script_info(self):
		"""
		Get the script info as a structure containing: Name, CompatibleTypes, Description, Version and the settings available.
		"""
		return await self._instance.gbx.execute('GetModeScriptInfo')

	async def set_script_name(self, name, instant=False):
		if instant:
			await self._instance.gbx.execute('SetModeScriptText', name)
		else:
			await self._instance.gbx.execute('SetScriptName', name)
		self._current_script = name

	async def get_settings(self):
		"""
		Get the current mode settings as a dictionary.
		"""
		return await self._instance.gbx.execute('GetModeScriptSettings')

	async def update_settings(self, update_dict):
		"""
		Update the current settings, merges current settings with the provided settings. Replaces by the keys you give
		if the data already exists.
		
		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		current_settings = await self.get_settings()
		current_settings.update(update_dict)
		await self._instance.gbx.execute('SetModeScriptSettings', current_settings)

	async def get_variables(self):
		"""
		Get the mode script variables.
		"""
		return await self._instance.gbx.execute('GetModeScriptVariables')

	async def update_variables(self, update_dict):
		"""
		Update the current variables, merges current vars with the provided vars. Replaces by the keys you give
		if the data already exists.
		
		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		variables = await self.get_variables()
		variables.update(update_dict)
		await self._instance.gbx.execute('SetModeScriptVariables', variables)
