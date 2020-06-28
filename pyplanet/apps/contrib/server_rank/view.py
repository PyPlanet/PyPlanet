from pyplanet.views.generics.list import ManualListView


class RankListView(ManualListView):
	title = 'Ranks on the server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'
	rank_list = []
	player = None

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': False,
				'searching': True,
				'width': 10,
				'type': 'label'
			},
			{
				'name': 'nickname',
				'index': 'nickname',
				'sorting': False,
				'searching': True,
				'width': 70,
				'type': 'label'
			},
			{
				'name': 'login',
				'index': 'login',
				'sorting': False,
				'searching': True,
				'width': 50,
				'type': 'label'
			},
			{
				'name': 'average',
				'index': 'avg',
				'sorting': False,
				'searching': True,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'difference',
				'index': 'diff',
				'sorting': False,
				'searching': True,
				'width': 50,
				'type': 'label'
			}
		]


	def __init__(self, app, player_index, data):
		super().__init__()
		self.app = app
		self.manager = app.context.ui
		self.player_index = player_index
		self.results = data

		self.provide_search = True
		self.provide_find_self = True
		self.subscribe('find_own', self._find_own)

	async def get_data(self):
		return self.results

	async def _find_own(self, player, *args, **kwargs):
		self.page = self.player_index // self.num_per_page + 1
		await self.refresh(player)
