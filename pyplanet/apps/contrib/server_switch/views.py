import logging

from pyplanet import __version__ as version
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.generics.widget import WidgetView
from pyplanet.utils import times
from pyplanet.contrib.player.exceptions import PlayerNotFound

logger = logging.getLogger(__name__)


class ServerswitchWidget(WidgetView):
	widget_x = 170
	widget_y = -40
	z_index = 60

	template_name = 'server_switch/server_switch.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_serverswitch'

