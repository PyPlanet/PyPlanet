from playhouse.shortcuts import model_to_dict

from pyplanet.apps.core.maniaplanet.models import Map
from pyplanet.views.generics import ManualListView


class TopRanksView(ManualListView):
	title = 'Top ranked players on the server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player, top_ranks):
		"""
		Init topsums list view.

		:param player: Player instance.
		:param app: App instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:type app: pyplanet.apps.contrib.rankings.Rankings
		"""
		super().__init__(self)

		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False
		self.top_ranks = top_ranks

	async def get_data(self):
		data = list()
		for idx, rank in enumerate(self.top_ranks):
			data.append(dict(
				rank=idx+1,
				player_nickname=rank.player.nickname,
				average='{:0.2f}'.format((rank.average / 10000))
			))

		return data

	async def destroy(self):
		self.top_ranks = None
		await super().destroy()

	def destroy_sync(self):
		self.top_ranks = None
		super().destroy_sync()

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'rank',
				'sorting': False,
				'searching': False,
				'width': 10,
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
				'name': 'Average',
				'index': 'average',
				'sorting': False,
				'searching': False,
				'width': 25,
				'type': 'label'
			}
		]


class NoRanksView(ManualListView):
	model = Map
	title = 'Non-ranked maps on this server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	def __init__(self, app, player, non_ranked_maps):
		"""
		Init no-rank list view.

		:param player: Player instance.
		:param app: App instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:type app: pyplanet.apps.contrib.rankings.Rankings
		"""
		super().__init__(self)

		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.non_ranked_maps = non_ranked_maps

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'width': 90,
				'type': 'label',
				'action': self.action_jukebox if ('jukebox' in self.app.instance.apps.apps) else None
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'width': 45,
			},
		]

	async def get_data(self):
		data = list()

		for non_ranked_map in self.non_ranked_maps:
			map_dict = model_to_dict(non_ranked_map)
			data.append(map_dict)

		return data

	async def action_jukebox(self, player, values, map_info, **kwargs):
		await self.app.instance.apps.apps['jukebox'].add_to_jukebox(player, await self.app.instance.map_manager.get_map(map_info['uid']))

