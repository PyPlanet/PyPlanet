from pyplanet.utils.times import format_time
from pyplanet.views.generics import ManualListView


class TopActivePlayersView(ManualListView):
	title = 'Top active players on the server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player, active):
		"""
		Init top active players list view.

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
		self.active = active

	async def get_data(self):
		data = list()
		for idx, player in enumerate(self.active):
			data.append(dict(
				place=idx+1,
				player_nickname=player.nickname,
				total_time=format_time(
					player.total_playtime * 1000, hide_hours_when_zero=False, hide_milliseconds=True
				),
			))

		return data

	async def destroy(self):
		self.active = None
		await super().destroy()

	def destroy_sync(self):
		self.active = None
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
				'width': 80,
				'type': 'label'
			},
			{
				'name': 'Total time on server',
				'index': 'total_time',
				'sorting': True,
				'searching': False,
				'width': 60,
				'type': 'label'
			},
		]


class TopDonatingPlayersView(ManualListView):
	title = 'Top donating players on the server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player, donators):
		"""
		Init top donating players list view.

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
		self.donators = donators

	async def get_data(self):
		return [dict(
			place=idx+1,
			player_nickname=player.nickname,
			total_donations=player.total_donations
		) for idx, player in enumerate(self.donators)]

	async def destroy(self):
		self.donators = None
		await super().destroy()

	def destroy_sync(self):
		self.donators = None
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
				'width': 80,
				'type': 'label'
			},
			{
				'name': 'Total donated amount of planets',
				'index': 'total_donations',
				'sorting': True,
				'searching': False,
				'width': 60,
				'type': 'label'
			},
		]
