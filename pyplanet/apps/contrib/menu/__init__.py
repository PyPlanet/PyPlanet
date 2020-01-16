from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from .views import MenuView


class Menu(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.menu = None
		self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)

	async def on_start(self):
		self.menu = MenuView(self)
		await self.menu.display()

	async def on_connect(self, player, *args, **kwargs):
		await self.menu.display(logins=[player.login])
