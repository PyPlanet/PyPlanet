
from pyplanet import __version__ as version
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.generics.widget import WidgetView
from pyplanet.utils import times
from pyplanet.contrib.player.exceptions import PlayerNotFound


class MapInfoWidget(WidgetView):
	widget_x = 125
	widget_y = 90

	template_name = 'info/mapinfo.xml'

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
			'map_author': map.author_login,
			'map_authortime': times.format_time(map.time_author) if map.time_author and map.time_author > 0 else '-',
			'map_environment': map.environment,
		})

		return context


class ServerInfoWidget(WidgetView):
	widget_x = -160
	widget_y = 90

	template_name = 'info/serverinfo.xml'

	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.info.Info
		"""
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_serverinfo'

	async def get_context_data(self):
		context = await super().get_context_data()

		ladder_min = int(self.app.instance.game.ladder_min)
		ladder_max = int(self.app.instance.game.ladder_max)

		if ladder_min > 1000:
			ladder_min = int(ladder_min / 1000)
		if ladder_max > 1000:
			ladder_max = int(ladder_max / 1000)

		context.update({
			'version': version,
			'num_players': self.app.instance.player_manager.count_players,
			'max_players': self.app.instance.player_manager.max_players,
			'num_spectators': self.app.instance.player_manager.count_spectators,
			'max_spectators': self.app.instance.player_manager.max_spectators,
			'ladder_min': ladder_min,
			'ladder_max': ladder_max,
		})

		return context
