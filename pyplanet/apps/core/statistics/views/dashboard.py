from .base import StatsView


class StatsDashboardView(StatsView):
	"""
	The Statistics Dashboard will show the summary of some statistics about the player and the server. The player can click
	on one of the 'More' buttons to show more detailed statistics about the subject.
	"""
	template_name = 'core.statistics/dashboard.xml'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.subscribe('button_close', self.close)

	async def get_context_data(self):
		context = await super().get_context_data()
		context['options'] = [
			dict(name='Top Records', view='pyplanet.apps.core.statistics.views.records.TopRecordsView'),
		]
		context['sizes'] = {
			'top__pos': '0 67',
			'top__size': '206.5 8',
			'box__size': '200 125',
			'bottom__pos': '0 -62',
			'bottom__size': '200 2',
			'input__pos': '0 -40',
			'input__size': '185 7',
		}
		return context

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])
		await self.destroy()
