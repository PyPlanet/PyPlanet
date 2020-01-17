from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from .views import GearView


class ViewGear(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.editor = None

	async def on_start(self):
		self.editor = GearView(self)
		await self.instance.command_manager.register(
			Command(command='gear', target=self.show_editor)
		)

	async def show_editor(self, player, data, **kwargs):
		await self.editor.display(player_logins=[player.login])
