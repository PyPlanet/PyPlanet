"""
Setting app component. Is part of the core contrib component 'setting'.
"""
from pyplanet.apps.core.pyplanet.views.setting import SettingMenuView
from pyplanet.contrib.command import Command


class SettingComponent:
	def __init__(self, app):
		"""
		Initiate setting component.

		:param app: App config instance
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		"""
		self.app = app

	async def on_init(self):
		pass

	async def on_start(self):
		await self.app.instance.permission_manager.register(
			'edit_server_settings', 'Edit server global settings.', app=self.app, min_level=3
		)

		await self.app.instance.command_manager.register(
			# Command('settings', self.player_settings, admin=False),
			Command('settings', self.admin_settings, perms='core.pyplanet:edit_server_settings', admin=True),
		)

	async def player_settings(self, player, *args, **kwargs):
		pass

	async def admin_settings(self, player, *args, **kwargs):
		await SettingMenuView(app=self.app, player=player).display()
