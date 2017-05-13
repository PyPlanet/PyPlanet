from pyplanet.apps.config import AppConfig

from pyplanet.apps.contrib.mapinfo.views import MapInfoWidget
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class MapInfo(AppConfig):
	name = 'pyplanet.apps.contrib.mapinfo'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.widget = None

	async def on_start(self):
		self.instance.signal_manager.listen(mp_signals.map.map_begin, self.map_begin)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)

		self.widget = MapInfoWidget(self)
		await self.widget.display()

	async def map_begin(self, map):
		await self.widget.display()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.widget.display(player=player)

