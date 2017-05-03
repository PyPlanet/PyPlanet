from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.statistics.tm import TrackmaniaComponent


class StatisticsConfig(AppConfig):
	name = 'pyplanet.apps.core.statistics'
	core = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate components.
		self.trackmania = TrackmaniaComponent(self)

	async def on_init(self):
		# Call components.
		await self.trackmania.on_init()

	async def on_start(self):
		# Call components.
		await self.trackmania.on_start()
