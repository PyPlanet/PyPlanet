
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.statistics.mp import ManiaplanetComponent
from pyplanet.apps.core.statistics.processor import StatisticsProcessor
from pyplanet.apps.core.statistics.tm import TrackmaniaComponent


class Statistics(AppConfig):
	core = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate components.
		self.processor = StatisticsProcessor(self)
		self.trackmania = TrackmaniaComponent(self)
		self.maniaplanet = ManiaplanetComponent(self)

	async def on_init(self):
		# Call components.
		if self.instance.game.game in ['tm', 'tmnext']:
			await self.trackmania.on_init()

		await self.maniaplanet.on_init()

	async def on_start(self):
		# Call components.
		if self.instance.game.game in ['tm', 'tmnext']:
			await self.trackmania.on_start()

		await self.maniaplanet.on_start()
