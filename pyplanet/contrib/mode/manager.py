import logging

from pyplanet.contrib import CoreContrib
from pyplanet.contrib.mode.signals import script_mode_changed

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
		self._current_script = await self.get_current_script(refresh=True)

		# Listeners.
		self._instance.signal_manager.listen('maniaplanet:server_start', self._on_change)

	async def _on_change(self, *args, **kwargs):
		# Making sure we set the settings + variables.
		if len(self._next_settings_update.keys()) > 0:
			logger.debug('Setting mode settings right now!')
			try:
				await self.update_settings(self._next_settings_update)
			except Exception as e:
				logging.error('Can\'t set the script mode settings! Error: {}'.format(str(e)))
			self._next_settings_update = dict()
		if len(self._next_variables_update.keys()) > 0:
			logger.debug('Setting mode variables right now!')
			try:
				await self.update_variables(self._next_variables_update)
			except Exception as e:
				logging.error('Can\'t set the script mode variables! Error: {}'.format(str(e)))
			self._next_variables_update = dict()

		# Make sure we send to the signal when mode is been changed.
		if self._current_script != self._next_script:
			await script_mode_changed.send_robust({
				'unloaded_script': self._current_script, 'loaded_script': self._next_script
			})

		await self.get_current_script(refresh=True)

	async def get_current_script(self, refresh=False):
		"""
		Get the current script name.

		:param refresh: Refresh from server.
		"""
		if refresh or not self._current_script:
			payload = await self._instance.gbx('GetScriptName')
			self._current_script = payload['CurrentValue'].partition('.')[0]
			if 'NextValue' in payload:
				self._next_script = payload['NextValue'].partition('.')[0]
		# if isinstance(self._current_script, str):
		# 	return self._current_script.lower()
		return self._current_script

	async def get_next_script(self, refresh=False):
		"""
		Get the next script name.

		:param refresh: Refresh from server.
		"""
		if refresh or not self._current_script:
			payload = await self._instance.gbx('GetScriptName')
			self._current_script = payload['CurrentValue'].partition('.')[0]
			if 'NextValue' in payload:
				self._next_script = payload['NextValue'].partition('.')[0]
		return self._next_script

	async def get_current_script_info(self):
		"""
		Get the script info as a structure containing: Name, CompatibleTypes, Description, Version and the settings available.
		"""
		return await self._instance.gbx('GetModeScriptInfo')

	async def set_next_script(self, name):
		"""
		Set the next played script name (after map restart/skip).

		:param name: Name
		"""
		await self._instance.gbx('SetScriptName', name)
		self._next_script = name.partition('.')[0]

	async def get_settings(self):
		"""
		Get the current mode settings as a dictionary.
		"""
		return await self._instance.gbx('GetModeScriptSettings')

	async def update_settings(self, update_dict):
		"""
		Update the current settings, merges current settings with the provided settings. Replaces by the keys you give
		if the data already exists.

		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		current_settings = await self.get_settings()
		current_settings.update(update_dict)
		await self._instance.gbx('SetModeScriptSettings', current_settings)

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
		return await self._instance.gbx('GetModeScriptVariables')

	async def update_variables(self, update_dict):
		"""
		Update the current variables, merges current vars with the provided vars. Replaces by the keys you give
		if the data already exists.

		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		variables = await self.get_variables()
		variables.update(update_dict)
		await self._instance.gbx('SetModeScriptVariables', variables)

	async def update_next_variables(self, update_dict):
		"""
		Queue variable changes for the next script (that will be active after restart).

		:param update_dict: The dictionary with the partial updated keys and values.
		"""
		if not isinstance(self._next_variables_update, dict):
			self._next_variables_update = dict()
		self._next_variables_update.update(update_dict)
