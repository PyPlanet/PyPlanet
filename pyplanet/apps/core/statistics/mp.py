"""
Maniaplanet app component.
"""
from pyplanet.apps.core.statistics.views.players import TopActivePlayersView, TopDonatingPlayersView
from pyplanet.contrib.command import Command


class ManiaplanetComponent:
	def __init__(self, app):
		"""
		Initiate maniaplanet statistics component.

		:param app: App config instance
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		self.app = app

	async def on_init(self):
		pass

	async def on_start(self):
		# Register commands.
		await self.app.instance.command_manager.register(
			Command('topactive', target=self.top_active,
					description='Displays the most active players on this server.'),
			Command('topdons', target=self.top_donators,
					description='Displays the players who donated the most planets to this server.'),
		)

	async def top_active(self, player, *args, **kwargs):
		view = TopActivePlayersView(self.app, player, await self.app.processor.get_top_active_players())
		await view.display(player)

	async def top_donators(self, player, *args, **kwargs):
		view = TopDonatingPlayersView(self.app, player, await self.app.processor.get_top_donating_players())
		await view.display(player)
