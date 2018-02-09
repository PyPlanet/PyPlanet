import asyncio
import logging
import os
import requests
from bs4 import BeautifulSoup
import urllib.request

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
			'music_server_url', 'Music Server Files URL', Setting.CAT_KEYS, type=str,
			description='Http link to directory where all song are. They must be in .ogg and downloadable',
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
			Command(command='song', target=self.get_current_song, admin=False),
			Command(command='songlist', target=self.song_list, admin=False)
		)

	async def song_list(self, player, *args, **kwargs):
		self.list = MusicListView(self)
		await self.list.display(player=player.login)

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
			await self.instance.gbx('SetForcedMusic', True, new_song[0])
		except Exception as e:
			await self.instance.chat(str(e))

	async def play_song(self, player, data, *args, **kwargs):
		song = str(data.songname)
		self.songs.insert(self.current_song+1, (song, await self.get_tags(song)))

	async def get_tags(self, song_url, *args, **kwargs):
		fs = str(urllib.request.urlopen(song_url).read(1000))
		# TODO: ADD HEADER USER AGENT
		tags = {
			'album': 'album',
			'albumartist': 'albumartist',
			'title': 'title',
			'artist': 'artist',
			'date': 'year',
			'tracknumber': 'track',
			'discnumber': 'disc',
			'genre': 'genre'
		}
		for key, value in tags.items():
			if fs.find(key.upper()) > 0:
				end_of_key = fs.find(key.upper()) + len(key) + 1
				end_of_value = fs.find('\\', fs.find(key.upper()))
				tags[key] = fs[end_of_key:end_of_value].replace(">", "")
		return tags

	async def get_songs(self):
		self.songs.clear()
		items = []
		if self.server.startswith("http"):
			page = requests.get(self.server).text
			soup = BeautifulSoup(page, 'html.parser')
			for node in soup.find_all('a'):
				if node.get('href').endswith('ogg'):
					song_url = (self.server + node.get('href')).replace("%20", " ")
					tags = await self.get_tags(self.server + node.get('href'))
					items.append((song_url, tags))
		return items

	async def get_current_song(self, player, *args, **kwargs):
		song_url, tags = self.songs[self.current_song]
		await self.instance.chat(song_url+" "+str(tags), player)
