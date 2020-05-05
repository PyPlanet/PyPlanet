from pyplanet.views.generics.widget import WidgetView

class TimerView(WidgetView):
	widget_x = 0
	widget_y = 0
	size_x = 0
	size_y = 0
	template_name = 'nightcup/timer.xml'

	def __init__(self, app):
		super().__init__()
		self.app = app
		self.manager = app.context.ui
