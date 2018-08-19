"""
ScriptSettings Admin methods and functions.
"""
import asyncio

from pyplanet.contrib.command import Command
from pyplanet.apps.contrib.admin.views.scriptsettings import ScriptSettingsView


class ScriptSettingsAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('scriptsettings', 'Manage script settings', app=self.app,
														min_level=2)

		await self.instance.command_manager.register(
			Command(command='script', target=self.script_settings, perms='admin:scriptsettings', admin=True)
		)

	async def script_settings(self, player, **kwargs):
		settings = await self.instance.mode_manager.get_settings()

		mode_info = await self.app.instance.mode_manager.get_current_script_info()
		descriptions = {}
		for info in mode_info['ParamDescs']:
			descriptions[info['Name']] = info['Desc']

		types = {}
		for key, value in settings.items():

			if isinstance(value, bool):
				types[key] = "bool"
			elif isinstance(value, float):
				types[key] = "float"
			elif isinstance(value, int):
				types[key] = "int"
			else:
				types[key] = "string"

		view = ScriptSettingsView(self.app, player, settings, descriptions, types)

		await view.display(player=player.login)
