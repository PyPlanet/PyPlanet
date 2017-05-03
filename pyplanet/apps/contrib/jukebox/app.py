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

		self.jukebox = []

	async def on_start(self):
		# Register permissions + commands.
		await self.instance.permission_manager.register('clear', 'Clear the jukebox', app=self, min_level=1)
		await self.instance.command_manager.register(
			Command(command='cjb', target=self.clear_jukebox, perms='jukebox:clear', admin=True),
			Command(command='clearjukebox', target=self.clear_jukebox, perms='jukebox:clear', admin=True),
			Command(command='list', target=self.show_map_list),
			Command(command='jukebox', target=self.chat_command).add_param(name='option', required=False)
		)

		# Register callback.
		self.instance.signal_manager.listen(mp_signals.flow.podium_start, self.podium_start)

	async def show_map_list(self, player, data, **kwargs):
		view = MapListView(self)
		await view.display(player=player.login)

	async def chat_command(self, player, data, **kwargs):
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
				message = '$z$s$fff» $i$f00There are currently no maps in the jukebox!'
				await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

		elif data.option == 'drop':
			first_player = next((item for item in reversed(self.jukebox) if item['player'].login == player.login), None)
			if first_player is not None:
				self.jukebox.remove(first_player)
				message = '$z$s$fff»» $fff{}$z$s$fa0 dropped $fff{}$z$s$fa0 from the jukebox.'.format(first_player['player'].nickname, first_player['map'].name)
				await self.instance.gbx.execute('ChatSendServerMessage', message)
			else:
				message = '$z$s$fff» $i$f00You currently don\'t have a map in the jukebox.'
				await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

		elif data.option == 'clear':
			if player.level == 0:
				message = '$z$s$fff» $i$f00You\'re not allowed to do this!'
				await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			else:
				await self.clear_jukebox(player, data)

	async def clear_jukebox(self, player, data, **kwargs):
		if len(self.jukebox) > 0:
			self.jukebox.clear()
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has cleared the jukebox.'.format(player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		else:
			message = '$z$s$fff» $i$f00There are currently no maps in the jukebox.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def add_to_jukebox(self, player, map):
		if player.level == 0 and any(item['player'].login == player.login for item in self.jukebox):
			message = '$z$s$fff» $i$f00You already have a map in the jukebox! Wait till it\'s been played before adding another.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			return

		if map.get_id() == self.instance.map_manager.current_map.get_id():
			message = '$z$s$fff» $i$f00You can\'t add the current map to the jukebox!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			return

		if not any(item['map'] == map for item in self.jukebox):
			self.jukebox.append({'player': player, 'map': map})
			message = '$z$s$fff»» $fff{}$z$s$fa0 was added to the jukebox by $fff{}$z$s$fa0.'.format(map.name, player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		else:
			message = '$z$s$fff» $i$f00This map has already been added to the jukebox, pick another one.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def drop_from_jukebox(self, player, instance):
		if player.level == 0 and instance['player_login'] != player.login:
			message = '$z$s$fff» $i$f00You can only drop your own jukeboxed maps!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
		else:
			drop_map = next((item for item in self.jukebox if item['map'].name == instance['map_name']), None)
			if drop_map is not None:
				self.jukebox.remove(drop_map)
				message = '$z$s$fff»» $fff{}$z$s$fa0 dropped $fff{}$z$s$fa0 from the jukebox.'.format(player.nickname, instance['map_name'])
				await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def podium_start(self, **kwargs):
		if len(self.jukebox) > 0:
			next = self.jukebox.pop(0)
			message = '$z$s$fff»» $fa0The next map will be $fff{}$z$s$fa0 as requested by $fff{}$z$s$fa0.'.format(next['map'].name, next['player'].nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
			await self.instance.map_manager.set_next_map(next['map'])
