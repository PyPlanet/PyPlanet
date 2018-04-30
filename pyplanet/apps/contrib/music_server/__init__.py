import asyncio
import async_timeout
import aiohttp
import re

from pyplanet.conf import settings
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command
from .view import MusicListView
from .view import PlaylistView


class MusicServer(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet', 'core.pyplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.lock = asyncio.Lock()
		self.context.signals.listen(mp_signals.map.map_end, self.map_end)
		self.server = None
		self.current_song_index = 0
		self.current_song = None
		self.songs = []
		self.list_view = None
		self.playlist = []
		self.playlist_view = None

	async def on_start(self):
		self.songs = await self.get_songs()
		self.list_view = MusicListView(self)
		self.playlist_view = PlaylistView(self)
		await self.instance.command_manager.register(
			Command(command='play', target=self.play_song, admin=True)
				.add_param(name='songname', type=str, required=True),
			Command(command='song', target=self.get_current_song, admin=False),
			Command(command='songlist', aliases='musiclist', target=self.song_list, admin=False),
			Command(command='playlist', target=self.show_playlist, admin=False),
			Command(command='clearplaylist', target=self.clear_playlist, admin=True),
		)
		self.current_song_index = -1

	async def song_list(self, player, *args, **kwargs):
		self.list_view = MusicListView(self)
		await self.list_view.display(player=player.login)

	async def insert_song(self, player, song):
		self.playlist = self.playlist + [{'player': player, 'song': song}]

	async def show_playlist(self, player, *args, **kwargs):
		self.playlist_view = PlaylistView(self)
		await self.playlist_view.display(player=player.login)

	async def add_to_playlist(self, player, song_index):
		async with self.lock:
			new_song = self.songs[song_index]
			if player.level == 0 and any(item['player'].login == player.login for item in self.playlist):
				message = '$i$f00You already have a song in the playlist! Wait till it\'s been played before adding another.'
				await self.instance.chat(message, player)
				return

			if not any(item['song'] == new_song for item in self.playlist):
				await self.insert_song(player.nickname, new_song)
				message = '$fff{}$z$s$fa0 was added to the playlist by $fff{}$z$s$fa0.'\
					.format(new_song[1]['artist']+" - "+new_song[1]['title'], player.nickname)
				await self.instance.chat(message)
			else:
				message = '$i$f00This song has already been added to the playlist, pick another one.'
				await self.instance.chat(message, player)

	async def drop_from_playlist(self, player, song_info):
		async with self.lock:
			if player.level == 0 and song_info['juke_player'] != player.nickname:
				message = '$i$f00You can only drop your own queued songs!'
				await self.instance.chat(message, player)
			else:
				drop_song = next((item for item in self.playlist if item['song'][1]['title'] == song_info['song_name']), None)
				if drop_song is not None:
					self.playlist.remove(drop_song)
					message = '$fff{}$z$s$fa0 dropped $fff{}$z$s$fa0 from the playlist.'\
						.format(player.nickname, song_info['song_name'])
					await self.instance.chat(message)

	async def map_end(self, *args, **kwargs):
		# Ignore when no songs are added.
		if not self.songs:
			return

		if self.playlist:
			new_song = self.playlist[0]['song']
			self.playlist.pop(0)
		else:
			if self.current_song_index + 2 > len(self.songs):
				new_song = self.songs[0]
				self.current_song_index = 0
			else:
				new_song = self.songs[self.current_song_index + 1]
				self.current_song_index += 1
		try:
			await self.instance.gbx('SetForcedMusic', True, new_song[0])
			self.current_song = new_song
		except Exception as e:
			await self.instance.chat(str(e))

	async def clear_playlist(self, player, data, **kwargs):
		async with self.lock:
			if len(self.playlist) > 0:
				self.playlist.clear()
				message = '$ff0Admin $fff{}$z$s$ff0 has cleared the playlist.'.format(player.nickname)
				await self.instance.chat(message)
			else:
				message = '$i$f00There are currently no songs in the playlist.'
				await self.instance.chat(message, player)

	async def play_song(self, player, data, *args, **kwargs):
		song = str(data.songname)
		try:
			async with aiohttp.ClientSession() as session:
				url, tags = (song, await self.get_tags(session, song))
				self.songs.insert(self.current_song_index + 1, (url, tags))
				message = '$fff{}$z$s$fa0 was added to the songlist by $fff{}$z$s$fa0.'\
					.format(tags['title']+" - "+tags['artist'], player.nickname)
				await self.instance.chat(message)
				await session.close()
		except Exception as e:
			await self.instance.chat(str(e), player)

	async def get_tags(self, session, url):
		with async_timeout.timeout(10):
			async with session.get(url) as response:
				fs = str(await response.content.read(1024))
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
						value = fs[end_of_key:end_of_value]
						if value.find('(') > 0 or value.find('[') > 0:
							tags[key] = re.sub(r'[^a-zA-Z\d\s\)\]]$', '', value)
						else:
							tags[key] = re.sub(r'[^a-zA-Z\d\s]*$', '', value)
			await response.release()
			return tags

	async def get_songs(self):
		setting = settings.SONGS
		if isinstance(setting, dict) and self.instance.process_name in setting:
			setting = setting[self.instance.process_name]
		if not isinstance(setting, list):
			setting = None

		if not setting:
			message = '$ff0Default song setting not configured in your settings file!'
			await self.instance.chat(message)
			return []

		self.songs.clear()
		songlist = setting
		async with aiohttp.ClientSession() as session:
			tags = [self.get_tags(session, song) for song in songlist]
			tag_list = await asyncio.gather(*tags)
		return [(song.replace("%20", " "), tag_list[i]) for i, song in enumerate(songlist)]

	async def get_current_song(self, player, *args, **kwargs):
		if self.current_song:
			song_url, tags = self.current_song
			message = '$ff0The current song is $fff{}$z$s$ff0 by $fff{}'.format(tags['title'], tags['artist'])
		else:
			message = '$i$f00There is no current song. Skip or restart!'
		await self.instance.chat(message, player)
