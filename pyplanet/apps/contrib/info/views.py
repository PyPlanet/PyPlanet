import logging

from pyplanet import __version__ as version
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.generics.widget import WidgetView
from pyplanet.utils import times
from pyplanet.contrib.player.exceptions import PlayerNotFound

logger = logging.getLogger(__name__)


class MapInfoWidget(WidgetView):
	widget_x = 125
	widget_y = 90
	z_index = 160

	template_name = 'info/mapinfo.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_mapinfo'

		self.mx_link_cache = dict()

	async def get_context_data(self):
		map = self.app.instance.map_manager.current_map

		# Load related info from other apps if installed and enabled, such as MX link.
		mx_link = None
		if 'mx' in self.app.instance.apps.apps:
			if map.uid in self.mx_link_cache:
				mx_link = self.mx_link_cache[map.uid]
			else:
				# Fetch, validate and make link.
				try:
					mx_info = await self.app.instance.apps.apps['mx'].api.map_info(map.uid)
					if mx_info and len(mx_info) >= 1:
						base_url = self.app.instance.apps.apps['mx'].api.base_url()
						mx_link = '{}/s/tr/{}'.format(
							base_url, mx_info[0][0]
						)
					self.mx_link_cache[map.uid] = mx_link
				except Exception as e:
					logger.error('Could not retrieve map info from MX/TM API for the info widget: {}'.format(str(e)))
					pass

		context = await super().get_context_data()
		context.update({
			'map_name': map.name,
			'map_mx_link': mx_link,
			'map_author': map.author_login,
			'map_authortime': times.format_time(map.time_author) if map.time_author and map.time_author > 0 else '-',
			'map_environment': map.environment,
		})

		return context


class ServerInfoWidget(WidgetView):
	widget_x = -160
	widget_y = 90
	z_index = 160

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
