from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from .views import MenuView


class Menu(AppConfig):
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.menu = None
		self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)

	async def on_start(self):
		self.menu = MenuView(self)
		await self.instance.command_manager.register(
			Command(command='menu', target=self.on_connect, admin=False))
		await self.menu.display()
		self.instance.ui_manager.properties.set_visibility('checkpoint_list', False)

	async def on_connect(self, player, *args, **kwargs):
		await self.menu.display(logins=[player.login])

