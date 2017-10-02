import asyncio
from xmlrpc.client import Fault

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.jukebox.views import MapListView, JukeboxListView, FolderListView, AddToFolderView
from pyplanet.apps.contrib.jukebox.folders import FolderManager
from pyplanet.contrib.command import Command

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.views.generics.alert import show_alert


class Jukebox(AppConfig):
	name = 'pyplanet.apps.contrib.jukebox'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.lock = asyncio.Lock()
		self.jukebox = []
		self.folder_manager = FolderManager(self)

	async def on_start(self):
		# Register permissions + commands.
		await self.instance.permission_manager.register('clear', 'Clear the jukebox', app=self, min_level=1)
		await self.instance.command_manager.register(
			Command(command='cjb', target=self.clear_jukebox, perms='jukebox:clear', admin=True),
			Command(command='clearjukebox', target=self.clear_jukebox, perms='jukebox:clear', admin=True),
			Command(command='list', target=self.show_map_list).add_param(name='search', required=False),
			Command(command='jukebox', target=self.chat_command).add_param(name='option', required=False),
			Command(command='mapfolders', target=self.show_map_folders)
		)

		# Register callback.
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)

		# Add button to the map list for adding to a folder.
		MapListView.add_action(self.add_to_folder, 'Add to folder', '&#xf07b;', order=-50)

		# Fetch all folders.
		await self.folder_manager.on_start()

	def insert_map(self, player, map):
		self.jukebox = [{'player': player, 'map': map}] + self.jukebox

	def append_map(self, player, map):
		self.jukebox.append({'player': player, 'map': map})

	def empty_jukebox(self):
		self.jukebox.clear()

	async def show_map_list(self, player, data, **kwargs):
		view = MapListView(self)
		if data.search is not None:
			view.search_text = data.search
		await view.display(player=player)

	async def show_map_folders(self, player, data, **kwargs):
		await self.folder_manager.display_folder_list(player)

	async def chat_command(self, player, data, **kwargs):
		if data.option is None:
			await self.display_chat_commands(player)
		else:
			async with self.lock:
				if data.option == 'list' or data.option == 'display':
					if len(self.jukebox) > 0:
						view = JukeboxListView(self)
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

				else:
					await self.display_chat_commands(player)

	async def display_chat_commands(self, player):
		message = '$ff0Available jukebox commands: $ffflist$ff0 | $fffdisplay$ff0 | $fffdrop$ff0'
		if player.level > 0:
			message += ' | $fffclear$ff0'
		message += '.'
		await self.instance.chat(message, player)

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

		# Try to set the map, if not successful it might be that the map is removed while juked!
		try:
			await asyncio.gather(
				self.instance.chat(message),
				self.instance.map_manager.set_next_map(next['map'])
			)
		except Fault as e:
			# It's removed from the server.
			if 'Map not in the selection' in e.faultString or 'Map unknown' in e.faultString:
				await self.instance.chat(
					'$fa0Setting the next map has been canceled because the map is not on the server anymore!'
				)

				# Retry the next map(s).
				await self.podium_start()
			else:
				raise

	async def add_to_folder(self, player, values, map_dictionary, view, **kwargs):
		view = AddToFolderView(self, player, map_dictionary['id'], self.folder_manager)
		await view.display()
		result = await view.wait_for_response()
		await view.destroy()

		if result:
			await show_alert(player, 'Map has been added to the folder!', 'sm')

	def add_maplist_action(self):
		pass

	def remove_maplist_action(self):
		pass
