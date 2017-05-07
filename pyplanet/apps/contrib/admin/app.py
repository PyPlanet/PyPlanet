from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.admin.map import MapAdmin
from pyplanet.apps.contrib.admin.player import PlayerAdmin
from pyplanet.apps.contrib.admin.server import ServerAdmin


class Admin(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.player = PlayerAdmin(self)
		self.map = MapAdmin(self)
		self.server = ServerAdmin(self)

	async def on_start(self):
		await self.player.on_start()
		await self.map.on_start()
		await self.server.on_start()
