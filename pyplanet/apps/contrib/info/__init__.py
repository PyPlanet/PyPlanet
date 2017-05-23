import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from . import views


class Info(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.map_widget = None
		self.server_widget = None

		self.update_pending = False

	async def on_start(self):
		self.instance.signal_manager.listen(mp_signals.map.map_begin, self.map_begin)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)
		self.instance.signal_manager.listen(mp_signals.player.player_disconnect, self.any_change)
		self.instance.signal_manager.listen(mp_signals.player.player_info_changed, self.any_change)

		# Move the multilapinfo a bit. (Only Trackmania).
		self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')
		self.instance.ui_manager.properties.set_visibility('map_info', False)

		self.map_widget = views.MapInfoWidget(self)
		self.server_widget = views.ServerInfoWidget(self)

		# Don't wait on the displaying of the widget.
		asyncio.ensure_future(self.map_widget.display())
		asyncio.ensure_future(self.server_widget.display())

		# Update server widget.
		asyncio.ensure_future(self.server_update_loop())

	async def server_update_loop(self):
		while True:
			await asyncio.sleep(5)
			try:
				if self.update_pending:
					await self.server_widget.display()
					self.update_pending = False
			except:
				pass

	async def map_begin(self, map):
		await asyncio.gather(
			self.map_widget.display(),
			self.server_widget.display()
		)

	async def player_connect(self, player, is_spectator, source, signal):
		await asyncio.gather(
			self.map_widget.display(player=player),
			self.server_widget.display(player=player)
		)
		self.update_pending = True

	async def any_change(self, **kwargs):
		self.update_pending = True
