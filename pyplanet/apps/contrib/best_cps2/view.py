from pyplanet.utils import times
from pyplanet.views.generics.list import ManualListView
from pyplanet.views.generics.widget import TimesWidgetView


class BestCpTimesWidget(TimesWidgetView):
	widget_x = -124.75
	widget_y = 90
	size_x = 250
	size_y = 18

	template_name = 'best_cps2/widget_top.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widget_bestcps'
		self.logins = []
		self.action = self.action_cptimeslist

	async def action_cptimeslist(self, player, **kwargs):
		view = CpTimesListView(self.app)
		await view.display(player=player.login)
		return view

	async def display(self, player=None, **kwargs):
		await super().display()


class CpTimesListView(ManualListView):
	title = 'Best CP times in current round'
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
	]

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.provide_search = False

	async def get_data(self):
		items = []
		list_times = self.app.best_cp_times
		for pcp in list_times:
			items.append({
				'index': pcp.cp,
				'player_nickname': pcp.player.nickname,
				'record_time': times.format_time(pcp.time)
			})

		return items
