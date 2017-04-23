from pyplanet.views.generics.list import ManualListView


class LocalRecordsListView(ManualListView):
	app = None

	title = 'Local Records on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	data = []

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.ui

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': True,
				'searching': False,
				'width': 10,
				'type': 'label'
			},
			{
				'name': 'Player',
				'index': 'player_nickname',
				'sorting': True,
				'searching': True,
				'width': 70
			},
			{
				'name': 'Time',
				'index': 'record_time',
				'sorting': True,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'Difference',
				'index': 'record_time_difference',
				'sorting': True,
				'searching': False,
				'width': 50,
				'type': 'label'
			},
		]
