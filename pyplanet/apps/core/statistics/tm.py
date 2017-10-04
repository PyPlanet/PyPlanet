"""
Trackmania app component.
"""
from pyplanet.apps.core.statistics.models import Score
from pyplanet.apps.core.statistics.views.dashboard import StatsDashboardView
from pyplanet.apps.core.statistics.views.score import StatsScoresListView
from pyplanet.apps.core.trackmania.callbacks import finish
from pyplanet.contrib.command import Command


class TrackmaniaComponent:
	def __init__(self, app):
		"""
		Initiate trackmania statistics component.

		:param app: App config instance
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		self.app = app

	async def on_init(self):
		pass

	async def on_start(self):
		# Listen to signals.
		self.app.context.signals.listen(finish, self.on_finish)

		# Register commands.
		# TODO: Finish work here!
		# await self.app.instance.command_manager.register(
		# 	Command('stats', target=self.open_stats)
		# )
		await self.app.instance.command_manager.register(
			Command(command='scoreprogression', aliases=['progression'], target=self.open_score_progression),
		)

	async def on_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		# Register the score of the player.
		await Score(
			player=player,
			map=self.app.instance.map_manager.current_map,
			score=race_time,
			checkpoints=','.join([str(cp) for cp in cps])
		).save()

	async def open_stats(self, player, **kwargs):
		view = StatsDashboardView(self.app, self.app.context.ui, player)
		await view.display()

	async def open_score_progression(self, player, **kwargs):
		view = StatsScoresListView(self.app, player)
		await view.display(player)
