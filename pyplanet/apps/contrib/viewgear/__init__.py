from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from .views import GearView
from pyplanet.apps.contrib.menu.signals import menu_add_entry


class ViewGear(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.gearview = None

	async def on_start(self):
		self.gearview = GearView(self)
		await self.instance.command_manager.register(
			Command(command='gear', target=self.show_gear)
		)
		await menu_add_entry.send({
			"icon": "",
			"menu_item": "View Gear",
			"category": "Generic",
			"level": 0,
			"callback": self.show_gear
		})

	async def show_gear(self, player, action, values, **kwargs):
		await self.gearview.display(player_logins=[player.login])
