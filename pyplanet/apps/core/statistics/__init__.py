
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.statistics.processor import StatisticsProcessor
from pyplanet.apps.core.statistics.tm import TrackmaniaComponent


class Statistics(AppConfig):
	core = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate components.
		self.processor = StatisticsProcessor(self)
		self.trackmania = TrackmaniaComponent(self)

	async def on_init(self):
		# Call components.
		if self.instance.game.game == 'tm':
			await self.trackmania.on_init()

	async def on_start(self):
		# Call components.
		if self.instance.game.game == 'tm':
			await self.trackmania.on_start()
