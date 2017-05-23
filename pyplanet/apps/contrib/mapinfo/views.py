"""
.. deprecated:: 0.4.0
	Use ``pyplanet.apps.contrib.info`` instead!
"""
from pyplanet.views.generics.widget import WidgetView
from pyplanet.utils import times
from pyplanet.contrib.player.exceptions import PlayerNotFound


class MapInfoWidget(WidgetView):
	widget_x = 125
	widget_y = 90

	template_name = 'mapinfo/mapinfo.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_mapinfo'

	async def get_context_data(self):
		map = self.app.instance.map_manager.current_map
		map_author = map.author_login
		try:
			author = await self.app.instance.player_manager.get_player(map.author_login)
			map_author = author.nickname
		except PlayerNotFound:
			if map.author_nickname:
				map_author = map.author_nickname

		context = await super().get_context_data()
		context.update({
			'map_name': map.name,
			'map_author': map_author,
			'map_authortime': times.format_time(map.time_author) if map.time_author and map.time_author > 0 else '-',
			'map_environment': map.environment,
		})

		return context
