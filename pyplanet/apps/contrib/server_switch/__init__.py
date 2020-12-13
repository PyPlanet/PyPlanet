import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.contrib.command import Command

from . import views

class Server_switch(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next', 'shootmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.serverswitch_widget = None

	async def on_start(self):
		
		await self.instance.command_manager.register(
			Command(command='qjoin', target=self.command_qjoin, admin=False, description='QuickJoin a other Server'))
		
		self.serverswitch_widget = views.ServerswitchWidget(self)
	
	async def command_qjoin(self, player, data, **kwargs):
		await asyncio.gather(
			self.serverswitch_widget.display(player=player),
			)


