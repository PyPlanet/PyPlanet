from pyplanet.views.generics.list import ManualListView


class KarmaListView(ManualListView):
	app = None

	title = 'Karma votes on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	data = []

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.ui

	async def get_fields(self):
		return [
			{
				'name': 'Player',
				'index': 'player_nickname',
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
