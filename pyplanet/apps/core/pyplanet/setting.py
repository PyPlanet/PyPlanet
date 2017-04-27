"""
Setting app component. Is part of the core contrib component 'setting'.
"""
import asyncio

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
		await self.app.instance.command_manager.register(
			# Command('settings', self.player_settings, admin=False),
			Command('settings', self.admin_settings, admin=True),
		)

	async def on_start(self):
		asyncio.ensure_future(self.call_later())
		pass

	async def call_later(self):
		await asyncio.sleep(2)
		await self.admin_settings(player=await self.app.instance.player_manager.get_player(login='tomvalk'))

	async def player_settings(self, player, *args, **kwargs):
		pass

	async def admin_settings(self, player, *args, **kwargs):
		await SettingMenuView(app=self.app, player=player).display()
