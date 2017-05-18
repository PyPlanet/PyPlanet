from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.apps.contrib.players.views import PlayerListView
from pyplanet.apps.core.maniaplanet.callbacks import player as player_signals
from pyplanet.contrib.setting import Setting


class Players(AppConfig):
	name = 'pyplanet.apps.contrib.players'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setting_enable_join_msg = Setting(
			'enable_join_message', 'Enable player join messages', Setting.CAT_FEATURES, type=bool, default=True,
			description='Enable this to announce that a player has joined the server.'
		)
		self.setting_enable_leave_msg = Setting(
			'enable_leave_message', 'Enable player leave messages', Setting.CAT_FEATURES, type=bool, default=True,
			description='Enable this to announce that a player has left the server.'
		)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='players', target=self.player_list)
		)
		await self.context.setting.register(
			self.setting_enable_join_msg, self.setting_enable_leave_msg
		)

		player_signals.player_connect.register(self.player_connect)
		player_signals.player_disconnect.register(self.player_disconnect)

	async def player_list(self, player, data, **kwargs):
		view = PlayerListView(self)
		await view.display(player=player.login)

	async def player_connect(self, player, **kwargs):
		if not await self.setting_enable_join_msg.get_value():
			return

		await self.instance.chat(
			'$ff0{} $fff{}$z$s$ff0 joined the server!'.format(player.get_level_string(), player.nickname)
		)

	async def player_disconnect(self, player, **kwargs):
		if not await self.setting_enable_leave_msg.get_value():
			return
		await self.instance.chat(
			'$ff0{} $fff{}$z$s$ff0 left the server!'.format(player.get_level_string(), player.nickname)
		)
