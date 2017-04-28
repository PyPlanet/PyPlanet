from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.apps.contrib.players.views import PlayerListView
from pyplanet.apps.core.maniaplanet.callbacks import player as player_signals


class Players(AppConfig):
	name = 'pyplanet.apps.contrib.players'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='players', target=self.player_list)
		)

		player_signals.player_connect.register(self.player_connect)
		player_signals.player_disconnect.register(self.player_disconnect)

	async def player_list(self, player, data, **kwargs):
		view = PlayerListView(self)
		await view.display(player=player.login)

	async def player_connect(self, player, **kwargs):
		await self.instance.gbx.execute(
			'ChatSendServerMessage',
			'$z$s$fff»» $ff0Player {}$z$s$ff0 joined the server!'.format(player.nickname)
		)
	async def player_disconnect(self, player, **kwargs):
		await self.instance.gbx.execute(
			'ChatSendServerMessage',
			'$z$s$fff»» $ff0Player {}$z$s$ff0 left the server!'.format(player.nickname)
		)
