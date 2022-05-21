from playhouse.shortcuts import model_to_dict

from pyplanet.apps.contrib.rankings import RankedMap
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


class MapListView(ManualListView):
	model = RankedMap
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	def __init__(self, app, player, maps, title, show_rank):
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
		self.maps = maps
		self.title = title
		self.show_rank = show_rank

	async def get_fields(self):
		columns = [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'width': 100,
				'type': 'label',
				'action': self.action_jukebox if ('jukebox' in self.app.instance.apps.apps) else None
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'renderer': lambda row, field:
				row['author_nickname']
				if 'author_nickname' in row and row['author_nickname'] and len(row['author_nickname'])
				else row['author_login'],
				'width': 60,
			},
		]

		if self.show_rank:
			columns.append({
				'name': 'Rank',
				'index': 'player_rank',
				'sorting': False,
				'searching': False,
				'search_strip_styles': False,
				'width': 15,
			})

		return columns

	async def get_data(self):
		data = list()

		for list_map in self.maps:
			data.append(model_to_dict(list_map))

		return data

	async def action_jukebox(self, player, values, map_info, **kwargs):
		await self.app.instance.apps.apps['jukebox'].add_to_jukebox(player, await self.app.instance.map_manager.get_map(map_info['uid']))

