from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.apps.contrib.players.views import PlayerListView


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

	async def player_list(self, player, data, **kwargs):
		view = PlayerListView(self)
		await view.display(player=player.login)
