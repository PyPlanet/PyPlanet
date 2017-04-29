from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.views.generics.list import ManualListView


class LocalRecordsWidget(TimesWidgetView):
	widget_x = 124
	#widget_x = -162
	widget_y = 48
	size_x = 38
	size_y = 55
	title = 'Local Records'
	icon_style = 'BgRaceScore2'
	icon_substyle = 'LadderRank'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_localrecords'

		self.action = self.action_recordlist

	async def get_player_data(self):
		data = await super().get_player_data()
		'''votes = dict()

		for player in self.app.instance.player_manager.online:
			player_vote = [x for x in self.app.current_votes if x.player_id == player.get_id()]
			if len(player_vote) > 0:
				votes[player.login] = {'player_vote': player_vote[0].score}
			else:
				votes[player.login] = {'player_vote': 0}

		data.update(votes)'''

		return data

	async def action_recordlist(self, player, **kwargs):
		await self.app.show_map_list(player)


class LocalRecordsListView(ManualListView):
	title = 'Local Records on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	fields = [
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
			'sorting': False,
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

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.ui
