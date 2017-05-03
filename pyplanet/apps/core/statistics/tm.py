"""
Trackmania app component.
"""
from pyplanet.apps.core.statistics.models import Score


class TrackmaniaComponent:
	def __init__(self, app):
		"""
		Initiate trackmania statistics component.

		:param app: App config instance
		:type app: pyplanet.apps.core.statistics.app.StatisticsConfig
		"""
		self.app = app

	async def on_init(self):
		pass

	async def on_start(self):
		# Listen to signals.
		self.app.instance.signal_manager.listen('trackmania:finish', self.on_finish)

	async def on_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		# Register the score of the player.
		Score.objects.create({
			'player': player,
			'map': self.app.instance.map_manager.current_map,
			'score': race_time,
			'checkpoints': ','.join(cps)
		})
