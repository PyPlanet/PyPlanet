from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.admin.map import MapAdmin
from pyplanet.apps.contrib.admin.player import PlayerAdmin
from pyplanet.apps.contrib.admin.server import ServerAdmin
from pyplanet.apps.contrib.admin.pyplanet import PyPlanetAdmin
from pyplanet.apps.contrib.admin.flow import FlowAdmin


class Admin(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.player = PlayerAdmin(self)
		self.map = MapAdmin(self)
		self.server = ServerAdmin(self)
		self.pyplanet = PyPlanetAdmin(self)
		self.flow = FlowAdmin(self)

	async def on_start(self):
		await self.player.on_start()
		await self.map.on_start()
		await self.server.on_start()
		await self.pyplanet.on_start()
		await self.flow.on_start()
