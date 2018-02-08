import asyncio
import logging
import os
import requests
from bs4 import BeautifulSoup

from pyplanet.contrib.setting import Setting
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command
from .view import MusicListView


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
		self.list = None

	async def on_start(self):
		await self.context.setting.register(
			self.setting_music_server_url_or_path
		)
		await self.reload_settings()
		self.list = MusicListView(self)
		await self.instance.command_manager.register(
			Command(command='play', target=self.play_song, admin=False)
				.add_param(name='songname', type=str, required=True),
			Command(command='playindex', target=self.play_index, admin=False)
				.add_param(name='index', type=int, required=True),
			Command(command='song', target=self.get_current_song, admin=False)
		)

	async def reload_settings(self, *args, **kwargs):
		self.server = await self.setting_music_server_url_or_path.get_value(refresh=True)
		self.songs = await self.get_songs()

	async def map_end(self, *args, **kwargs):
		if self.current_song+1 > len(self.songs):
			new_song = self.songs[0]
			self.current_song = 0
		else:
			new_song = self.songs[self.current_song+1]
			self.current_song += 1
		try:
			await self.instance.gbx('SetForcedMusic', True, new_song)
		except Exception as e:
			await self.instance.chat(str(e))

	async def play_song(self, player, data, *args, **kwargs):
		song = str(data.songname)
		await self.instance.chat(song, player)
		await self.instance.gbx('SetForcedMusic', True, song)
		await self.instance.chat("song " + song + " started playing", player)

	async def play_index(self, player, data, *args, **kwargs):
		if data == 0:
			for song in self.songs:
				try:
					# await self.instance.gbx('SetForcedMusic', True, song)
					await self.instance.chat(song, player)
				except Exception as e:
					await self.instance.chat(str(e))
		else:
			await self.list.display(player=player.login)

	async def get_songs(self):
		if self.server.startswith("http"):
			page = requests.get(self.server).text
			soup = BeautifulSoup(page, 'html.parser')
			return [(self.server + node.get('href')).replace("%20", " ") for node in soup.find_all('a') if node.get('href').endswith('ogg')]
		elif self.server:
			path = os.path.join('GameData', self.server.replace("/", "").replace("\\", ""))
			if await self.instance.storage.driver.exists(path):
				return await self.instance.storage.driver.listdir(path)

	async def get_current_song(self, player, *args, **kwargs):
		await self.instance.chat(self.songs[self.current_song], player)
