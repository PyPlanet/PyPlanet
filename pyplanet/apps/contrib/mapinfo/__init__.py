"""
.. deprecated:: 0.4.0
	Use ``pyplanet.apps.contrib.info`` instead!
"""
# TODO: Remove in 0.7.0.

import logging
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.utils import style
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from . import views


class MapInfo(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.map_widget = None

	async def output_deprecated(self):
		msg = [
			'$f00$o\uf0a1 $z$s$f00$o$wDEPRECATION:$z$s$f55$o Please change your settings! $z$f55$s(\uf121 apps.py)',
			'$f55Replace \'pyplanet.apps.contrib.mapinfo\' by \'pyplanet.apps.contrib.info\'.',
			'$f55MapInfo will be removed in $o0.7.0$o and will break your installation!'
		]
		for m in msg:
			logging.error(style.style_strip(m))
		await self.instance.chat.execute(*msg)

	async def on_start(self):
		self.instance.signal_manager.listen(mp_signals.map.map_begin, self.map_begin)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)

		# Move the multilapinfo a bit. (Only Trackmania).
		self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')
		self.instance.ui_manager.properties.set_visibility('map_info', False)

		self.map_widget = views.MapInfoWidget(self)

		# Don't wait on the displaying of the widget.
		asyncio.ensure_future(self.map_widget.display())

		await self.output_deprecated()

	async def map_begin(self, map):
		await self.map_widget.display()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.map_widget.display(player=player)
		if player.level > 0:
			await self.output_deprecated()
