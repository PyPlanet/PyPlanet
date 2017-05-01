import logging

from pyplanet.contrib import CoreContrib

logger = logging.getLogger(__name__)


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
		self._next_script = None

		self._next_settings_update = dict()
		self._next_variables_update = dict()

	async def on_start(self):
		"""
		Handle startup, just before the apps will start. We will make sure we are ready to get requests for permissions.
		"""
		self._current_script = await self.get_current_script()

		# Listeners.
		self._instance.signal_manager.listen('maniaplanet:server_start', self._on_change)

	async def _on_change(self, *args, **kwargs):
		if len(self._next_settings_update.keys()) > 0:
			logger.debug('Setting mode settings right now!')
			await self.update_settings(self._next_settings_update)
			self._next_settings_update = dict()
		if len(self._next_variables_update.keys()) > 0:
			logger.debug('Setting mode variables right now!')
			await self.update_variables(self._next_variables_update)
			self._next_variables_update = dict()
		await self.get_current_script(refresh=True)

	async def get_current_script(self, refresh=False):
		"""
		Get the current script name.
		
		:param refresh: Refresh from server.
		"""
		if refresh or not self._current_script:
			payload = await self._instance.gbx.execute('GetScriptName')
			self._current_script = payload['CurrentValue']
			if 'NextValue' in payload:
				self._next_script = payload['NextValue']
		return self._current_script

	async def get_next_script(self, refresh=False):
		"""
		Get the next script name.
		
		:param refresh: Refresh from server.
		"""
		if refresh or not self._current_script:
			payload = await self._instance.gbx.execute('GetScriptName')
			self._current_script = payload['CurrentValue']
			if 'NextValue' in payload:
				self._next_script = payload['NextValue']
		return self._next_script

	async def get_current_script_info(self):
		"""
		Get the script info as a structure containing: Name, CompatibleTypes, Description, Version and the settings available.
		"""
		return await self._instance.gbx.execute('GetModeScriptInfo')

	async def set_next_script(self, name):
		"""
		Set the next played script name (after map restart/skip).
		
		:param name: Name
		"""
		await self._instance.gbx.execute('SetScriptName', name)
		self._next_script = name

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

	async def update_next_settings(self, update_dict):
		"""
		Queue setting changes for the next script (that will be active after restart).
		
		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		if not isinstance(self._next_settings_update, dict):
			self._next_settings_update = dict()
		self._next_settings_update.update(update_dict)

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

	async def update_next_variables(self, update_dict):
		"""
		Queue variable changes for the next script (that will be active after restart).
		
		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		if not isinstance(self._next_variables_update, dict):
			self._next_variables_update = dict()
		self._next_variables_update.update(update_dict)
