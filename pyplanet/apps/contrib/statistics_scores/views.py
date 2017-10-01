from pyplanet.views.generics.list import ManualListView


class ScoresListView(ManualListView):
	title = 'Personal time progression on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	scores = []

	def __init__(self, app, scores):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.scores = scores
		self.provide_search = False

	async def get_data(self):
		return self.scores

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': False,
				'searching': False,
				'width': 6,
				'type': 'label'
			},
			{
				'name': 'Time',
				'index': 'score',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'From PB',
				'index': 'difference_to_pb',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'From previous PB',
				'index': 'difference_to_prev',
				'sorting': False,
				'searching': False,
				'width': 34,
				'type': 'label'
			},
			{
				'name': 'Driven at',
				'index': 'created_at',
				'sorting': False,
				'searching': False,
				'width': 40,
				'type': 'label'
			},
		]
