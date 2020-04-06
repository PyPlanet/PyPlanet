"""
Toolbar app component
"""
from pyplanet.apps.core.pyplanet.views.setting import SettingMenuView
from pyplanet.apps.core.pyplanet.views.toolbar import ToolbarView
from pyplanet.contrib.setting import Setting

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class ToolbarComponent:
	def __init__(self, app):
		"""
		Initiate toolbar component.

		:param app: App config instance
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		"""
		self.app = app

		self.setting_display_toolbar = Setting(
			'display_player_toolbar', 'Display player toolbar', Setting.CAT_DESIGN, type=bool, default=True,
			description='Display the toolbar to all the players, the toolbar contains some useful buttons',
			change_target=self.reload_settings
		)

		self.widget = ToolbarView(self.app)

	async def on_init(self):
		pass

	async def reload_settings(self, *args, **kwargs):
		if await self.setting_display_toolbar.get_value():
			await self.widget.display()
		else:
			await self.widget.hide()

	async def on_start(self):
		await self.app.context.setting.register(
			self.setting_display_toolbar
		)

		self.app.context.signals.listen(mp_signals.player.player_connect, self.player_connect)

		if await self.setting_display_toolbar.get_value():
			await self.widget.display()

	async def player_connect(self, player, *args, **kwargs):
		if await self.setting_display_toolbar.get_value():
			await self.widget.display(player_logins=[player.login])
