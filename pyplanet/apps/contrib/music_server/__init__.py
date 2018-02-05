import asyncio
import logging
import requests
from bs4 import BeautifulSoup

from pyplanet.contrib.setting import Setting
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command


class MusicServer(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet', 'core.pyplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setting_music_server_url_or_path = Setting(
			'music_server_url_or_path', 'Music Files Path or URL', Setting.CAT_KEYS, type=str,
			description='Local Path below "GameData" or http link to directory where all files must be downloadable',
			default='http://5.230.142.8/tm/music/', change_target=self.reload_settings
		)
		self.context.signals.listen(mp_signals.map.map_end, self.map_end)
		self.server = None
		self.current_song = 0
		self.songs = []

	async def on_start(self):
		await self.instance.setting_manager.register(
			self.setting_music_server_url_or_path
		)
		await self.reload_settings()
		if self.server:
			self.songs = await self.get_songs(self.server)

		await self.instance.command_manager.register(
			Command(command='play', target=self.play_song, admin=False)
				.add_param(name='songname', type=str, required=True),
			Command(command='playindex', target=self.play_index, admin=False)
				.add_param(name='index', type=int, required=True)
		)

	async def reload_settings(self, *args, **kwargs):
		self.server = await self.setting_music_server_url_or_path.get_value(refresh=True)

	async def map_end(self, *args, **kwargs):
		if self.current_song+1 > len(self.songs):
			new_song = self.songs[0]
			self.current_song = 0
		else:
			new_song = self.songs[self.current_song+1]
			self.current_song += 1
		await self.instance.gbx('SetForcedMusic', True, new_song)

	async def play_song(self, player, data, *args, **kwargs):
		song = data.songname
		await self.instance.gbx('SetForcedMusic', True, song)
		await self.instance.chat("song " + song + " started playing", player)

	async def play_index(self, player, data, *args, **kwargs):
		song = self.songs[data.index]
		await self.instance.gbx('SetForcedMusic', True, song)
		await self.instance.gbx('NextMap')

	async def get_songs(self, url):
		page = requests.get(url).text
		soup = BeautifulSoup(page, 'html.parser')
		return [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith('ogg')]
