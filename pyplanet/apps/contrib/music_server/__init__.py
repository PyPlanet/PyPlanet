import asyncio
import logging

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command


class MusicServer(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet', 'core.pyplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='play', target=self.play_song, admin=False)
				.add_param(name='songname', type=str, required=True)
		)

	async def play_song(self, player, data, *args, **kwargs):
		song = data.songname
		await self.instance.gbx('SetForcedMusic', True, song)
		await self.instance.chat("song "+song+" started playing", player)

