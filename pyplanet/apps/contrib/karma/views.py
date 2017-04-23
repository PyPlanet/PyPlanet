from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.generics.list import ManualListView


class KarmaListView(ManualListView):
	title = 'Karma votes on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	fields = [
		{
			'name': 'Player',
			'index': 'nickname',
			'sorting': False,
			'searching': True,
			'width': 70
		},
		{
			'name': 'Vote',
			'index': 'vote',
			'sorting': True,
			'searching': False,
			'width': 30,
			'type': 'label'
		}
	]

	def __init__(self, app, map):
		super().__init__(self)
		self.app = app
		self.manager = app.ui
		self.map = map

	async def get_title(self):
		return 'Karma votes on {}'.format(self.map.name)

	async def get_data(self):
		karma = await Karma.execute(
			Karma
				.select(Karma, Player)
				.join(Player)
				.where(Karma.map == self.map)
		)
		return [
			{'nickname': item.player.nickname, 'vote': '++' if item.score else '--'} for item in karma
		]
