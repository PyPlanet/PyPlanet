from pyplanet.views.generics.widget import WidgetView
from pyplanet.utils import times


class MapInfoWidget(WidgetView):
	widget_x = 124
	widget_y = 90.5
	size_x = 38
	size_y = 14
	title = None  # 'Current map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Challenge'

	template_name = 'mapinfo/mapinfo.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_mapinfo'

	async def get_context_data(self):
		map = self.app.instance.map_manager.current_map

		context = await super().get_context_data()
		context.update({
			'map_name': map.name,
			'map_author': map.author_nickname if map.author_nickname is not None else map.author_login,
			'map_authortime': times.format_time(map.time_author),
			'map_environment': map.environment,
		})

		return context
