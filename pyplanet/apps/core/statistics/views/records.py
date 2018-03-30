from pyplanet.views.generics import ManualListView
from .base import StatsView


class TopRecordsView(StatsView):
	template_name = 'core.statistics/menu.xml'

	async def get_context_data(self):
		context = await super().get_context_data()
		context['options'] = [
			dict(name='Top Records', view='pyplanet.apps.core.statistics.views.records.TopRecords'),
		]


class TopSumsView(ManualListView):
	title = 'Top players on the server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player, topsums):
		"""
		Init topsums list view.

		:param player: Player instance.
		:param app: App instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		super().__init__(self)

		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False
		self.topsums = topsums

	async def get_data(self):
		data = list()
		for idx, (player, (first, second, third)) in enumerate(self.topsums):
			data.append(dict(
				place=idx+1,
				player_nickname=player.nickname,
				first=first,
				second=second,
				third=third,
				total=first + second + third,
			))

		return data

	async def destroy(self):
		self.topsums = None
		await super().destroy()

	def destroy_sync(self):
		self.topsums = None
		super().destroy_sync()

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'place',
				'sorting': False,
				'searching': False,
				'width': 6,
				'type': 'label'
			},
			{
				'name': 'Player',
				'index': 'player_nickname',
				'sorting': False,
				'searching': False,
				'width': 60,
				'type': 'label'
			},
			{
				'name': '1st local',
				'index': 'first',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
			{
				'name': '2nd local',
				'index': 'second',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
			{
				'name': '3rd local',
				'index': 'third',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
			{
				'name': 'total top 3',
				'index': 'total',
				'sorting': True,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
		]
