from pyplanet.views.generics.widget import TimesWidgetView


class BestCpTimesWidget(TimesWidgetView):
	widget_x = -124
	widget_y = 90
	size_x = 240
	size_y = 20
	title = 'Best CPs'

	template_name = 'best_cps/widget_top.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widget_bestcps'
		self.logins = []

	async def display(self, player=None, **kwargs):
		await super().display()
