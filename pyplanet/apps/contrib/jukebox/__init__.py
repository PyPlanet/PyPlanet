import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.jukebox.views import MapListView, JukeboxListView
from pyplanet.contrib.command import Command

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class Jukebox(AppConfig):
	name = 'pyplanet.apps.contrib.jukebox'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.lock = asyncio.Lock()
		self.jukebox = []

	async def on_start(self):
		# Register permissions + commands.
		await self.instance.permission_manager.register('clear', 'Clear the jukebox', app=self, min_level=1)
		await self.instance.command_manager.register(
			Command(command='cjb', target=self.clear_jukebox, perms='jukebox:clear', admin=True),
			Command(command='clearjukebox', target=self.clear_jukebox, perms='jukebox:clear', admin=True),
			Command(command='list', target=self.show_map_list).add_param(name='search', required=False),
			Command(command='jukebox', target=self.chat_command).add_param(name='option', required=False)
		)

		# Register callback.
		self.instance.signal_manager.listen(mp_signals.flow.podium_start, self.podium_start)

	def insert_map(self, player, map):
		self.jukebox = [{'player': player, 'map': map}] + self.jukebox

	def append_map(self, player, map):
		self.jukebox.append({'player': player, 'map': map})

	def clear_jukebox(self):
		self.jukebox.clear()

	async def show_map_list(self, player, data, **kwargs):
		view = MapListView(self)
		if data.search is not None:
			view.search_text = data.search
		await view.display(player=player.login)

	async def chat_command(self, player, data, **kwargs):
		async with self.lock:
			if data.option == 'list' or data.option == 'display':
				if len(self.jukebox) > 0:
					index = 1
					view = JukeboxListView(self)
					view_data = []
					for item in self.jukebox:
						view_data.append({'index': index, 'map_name': item['map'].name, 'player_nickname': item['player'].nickname, 'player_login': item['player'].login})
						index += 1
					view.objects_raw = view_data
					await view.display(player=player.login)
				else:
					message = '$i$f00There are currently no maps in the jukebox!'
					await self.instance.chat(message, player)

			elif data.option == 'drop':
				first_player = next((item for item in reversed(self.jukebox) if item['player'].login == player.login), None)
				if first_player is not None:
					self.jukebox.remove(first_player)
					message = '$fff{}$z$s$fa0 dropped $fff{}$z$s$fa0 from the jukebox.'.format(first_player['player'].nickname, first_player['map'].name)
					await self.instance.chat(message)
				else:
					message = '$i$f00You currently don\'t have a map in the jukebox.'
					await self.instance.chat(message, player)

			elif data.option == 'clear':
				if player.level == 0:
					message = '$i$f00You\'re not allowed to do this!'
					await self.instance.chat(message, player)
				else:
					await self.clear_jukebox(player, data)

	async def clear_jukebox(self, player, data, **kwargs):
		async with self.lock:
			if len(self.jukebox) > 0:
				self.jukebox.clear()
				message = '$ff0Admin $fff{}$z$s$ff0 has cleared the jukebox.'.format(player.nickname)
				await self.instance.chat(message)
			else:
				message = '$i$f00There are currently no maps in the jukebox.'
				await self.instance.chat(message, player)

	async def add_to_jukebox(self, player, map):
		async with self.lock:
			if player.level == 0 and any(item['player'].login == player.login for item in self.jukebox):
				message = '$i$f00You already have a map in the jukebox! Wait till it\'s been played before adding another.'
				await self.instance.chat(message, player)
				return

			if map.get_id() == self.instance.map_manager.current_map.get_id() and player.level == 0:
				message = '$i$f00You can\'t add the current map to the jukebox!'
				await self.instance.chat(message, player)
				return

			if not any(item['map'] == map for item in self.jukebox):
				self.jukebox.append({'player': player, 'map': map})
				message = '$fff{}$z$s$fa0 was added to the jukebox by $fff{}$z$s$fa0.'.format(map.name, player.nickname)
				await self.instance.chat(message)
			else:
				message = '$i$f00This map has already been added to the jukebox, pick another one.'
				await self.instance.chat(message, player)

	async def drop_from_jukebox(self, player, instance):
		async with self.lock:
			if player.level == 0 and instance['player_login'] != player.login:
				message = '$i$f00You can only drop your own jukeboxed maps!'
				await self.instance.chat(message, player)
			else:
				drop_map = next((item for item in self.jukebox if item['map'].name == instance['map_name']), None)
				if drop_map is not None:
					self.jukebox.remove(drop_map)
					message = '$fff{}$z$s$fa0 dropped $fff{}$z$s$fa0 from the jukebox.'.format(player.nickname, instance['map_name'])
					await self.instance.chat(message)

	async def podium_start(self, **kwargs):
		if len(self.jukebox) == 0:
			return
		next = self.jukebox.pop(0)
		message = '$fa0The next map will be $fff{}$z$s$fa0 as requested by $fff{}$z$s$fa0.'.format(next['map'].name, next['player'].nickname)
		await asyncio.gather(
			self.instance.chat(message),
			self.instance.map_manager.set_next_map(next['map'])
		)

	def add_maplist_action(self):
		pass

	def remove_maplist_action(self):
		pass
