from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.jukebox.views import MapListView
from pyplanet.core.events import receiver
from pyplanet.contrib.command import Command

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

class JukeboxConfig(AppConfig):
	name = 'pyplanet.apps.contrib.jukebox'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.jukebox = []

	async def on_start(self):
		self.match_end()

		await self.instance.permission_manager.register('next', 'Skip to the next map', app=self, min_level=1)

		self.instance.command_manager.commands.extend([Command(command='list', target=self.show_map_list)])
		self.instance.command_manager.commands.extend([Command(command='next', target=self.skip_map, perms='jukebox:next', admin=True)])
		jukebox_command = Command(command='jukebox', target=self.chat_command)
		jukebox_command.add_param(name='option', required=False)
		self.instance.command_manager.commands.extend([jukebox_command])

	async def show_map_list(self, player, data, **kwargs):
		view = MapListView(self)
		await view.display(player=player.login)

	async def skip_map(self, player, data, **kwargs):
		await self.instance.gbx.execute('NextMap')

	async def chat_command(self, player, data, **kwargs):
		if data.option == 'list' or data.option == 'display':
			jukebox_items = []
			index = 1
			for item in self.jukebox:
				jukebox_items.append('$fff{}.$fa0 [$fff{}$z$s$fa0]'.format(index, item['map'].name))
				index += 1

			if len(jukebox_items) > 0:
				jukebox_items_chat = ' '.join(jukebox_items)

				message = '$z$s> $fa0Currently in the jukebox: {}'.format(jukebox_items_chat)
				await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			else:
				message = '$z$s> $fa0There are currently no maps in the jukebox!'
				await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

		elif data.option == 'drop':
			first_player = next((item for item in reversed(self.jukebox) if item['player'].login == player.login), None)
			if first_player is not None:
				self.jukebox.remove(first_player)
				message = '$z$s> $fff{}$z$s$fa0 dropped $fff{}$z$s$fa0 from the jukebox.'.format(first_player['player'].nickname, first_player['map'].name)
				await self.instance.gbx.execute('ChatSendServerMessage', message)
			else:
				message = '$z$s> $fa0You currently don\'t have a map in the jukebox.'
				await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def add_to_jukebox(self, player, map):
		if player.level == 0 and any(item['player'].login == player.login for item in self.jukebox):
			message = '$z$s> $fa0You already have a map in the jukebox! Wait till it\'s been played before adding another.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			return

		if not any(item['map'] == map for item in self.jukebox):
			self.jukebox.append({'player': player, 'map': map})
			message = '$z$s> $fff{}$z$s$fa0 was added to the jukebox by $fff{}$z$s$fa0.'.format(map.name, player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		else:
			message = '$z$s> $fa0This map has already been added to the jukebox, pick another one.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	@receiver(mp_signals.flow.podium_start)
	async def match_end(self, **kwargs):
		if len(self.jukebox) > 0:
			next = self.jukebox.pop(0)
			print(next)
			message = '$z$s> $fa0The next map will be $fff{}$z$s$fa0 as requested by $fff{}$z$s$fa0.'.format(next['map'].name, next['player'].nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
			await self.instance.map_manager.set_next_map(next['map'])
