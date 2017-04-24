from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.contrib.player.exceptions import PlayerNotFound


class AdminConfig(AppConfig):
	name = 'pyplanet.apps.contrib.admin'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.permission_manager.register('next', 'Skip to the next map', app=self, min_level=1)
		await self.instance.permission_manager.register('restart', 'Restart the maps', app=self, min_level=1)

		await self.instance.permission_manager.register('ignore', 'Ignore a player', app=self, min_level=1)
		await self.instance.permission_manager.register('unignore', 'Unignore a player', app=self, min_level=1)
		await self.instance.permission_manager.register('kick', 'Kick a player', app=self, min_level=1)
		await self.instance.permission_manager.register('ban', 'Ban a player', app=self, min_level=2)
		await self.instance.permission_manager.register('unban', 'Unban a player', app=self, min_level=2)

		await self.instance.permission_manager.register('password', 'Set the server passwords', app=self, min_level=2)

		await self.instance.command_manager.register(
			Command(command='next', target=self.next_map, perms='admin:next', admin=True),
			Command(command='skip', target=self.next_map, perms='admin:next', admin=True),
			Command(command='restart', target=self.restart_map, perms='admin:restart', admin=True),
			Command(command='res', target=self.restart_map, perms='admin:restart', admin=True),
			Command(command='rs', target=self.restart_map, perms='admin:restart', admin=True),

			Command(command='mute', target=self.ignore_player, perms='admin:ignore', admin=True).add_param(name='login', required=True),
			Command(command='ignore', target=self.ignore_player, perms='admin:ignore', admin=True).add_param(name='login', required=True),
			Command(command='unmute', target=self.unignore_player, perms='admin:unignore', admin=True).add_param(name='login', required=True),
			Command(command='unignore', target=self.unignore_player, perms='admin:unignore', admin=True).add_param(name='login', required=True),
			Command(command='kick', target=self.kick_player, perms='admin:kick', admin=True).add_param(name='login', required=True),
			Command(command='ban', target=self.ban_player, perms='admin:ban', admin=True).add_param(name='login', required=True),
			Command(command='unban', target=self.unban_player, perms='admin:unban', admin=True).add_param(name='login', required=True),

			Command(command='setpassword', target=self.set_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='srvpass', target=self.set_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='setspecpassword', target=self.set_spec_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='spectpass', target=self.set_spec_password, perms='admin:password', admin=True).add_param(name='password', required=False)
		)

	async def next_map(self, player, data, **kwargs):
		await self.instance.gbx.execute('NextMap')
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has skipped to the next map.'.format(player.nickname)
		await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def restart_map(self, player, data, **kwargs):
		await self.instance.gbx.execute('RestartMap')
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has restarted the map.'.format(player.nickname)
		await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def ignore_player(self, player, data, **kwargs):
		try:
			mute_player = await self.instance.player_manager.get_player(data.login)
			await self.instance.gbx.execute('Ignore', data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has muted $fff{}$z$s$ff0.'.format(player.nickname, mute_player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def unignore_player(self, player, data, **kwargs):
		try:
			unmute_player = await self.instance.player_manager.get_player(data.login)
			await self.instance.gbx.execute('UnIgnore', data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has un-muted $fff{}$z$s$ff0.'.format(player.nickname, unmute_player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def kick_player(self, player, data, **kwargs):
		try:
			kick_player = await self.instance.player_manager.get_player(data.login)
			await self.instance.gbx.execute('Kick', data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has kicked $fff{}$z$s$ff0.'.format(player.nickname, kick_player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def ban_player(self, player, data, **kwargs):
		try:
			ban_player = await self.instance.player_manager.get_player(data.login)
			await self.instance.gbx.execute('Ban', data.login)
			await self.instance.gbx.execute('Kick', data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has banned $fff{}$z$s$ff0.'.format(player.nickname, ban_player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def unban_player(self, player, data, **kwargs):
		await self.instance.gbx.execute('UnBan', data.login)
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has un-banned $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def blacklist_player(self, player, data, **kwargs):
		try:
			blacklist_player = await self.instance.player_manager.get_player(data.login)
			await self.instance.gbx.execute('BlackList', data.login)
			await self.instance.gbx.execute('Kick', data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has blacklisted $fff{}$z$s$ff0.'.format(player.nickname, blacklist_player.nickname)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def unblacklist_player(self, player, data, **kwargs):
		await self.instance.gbx.execute('UnBlackList', data.login)
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has un-blacklisted $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def set_password(self, player, data, **kwargs):
		if data.password is None or data.password == 'none':
			await self.instance.gbx.execute('SetServerPassword', '')
			message = '$z$s$fff» $ff0You removed the server password.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
		else:
			await self.instance.gbx.execute('SetServerPassword', data.password)
			message = '$z$s$fff» $ff0You changed the server password to: "$fff{}$ff0".'.format(data.password)
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def set_spec_password(self, player, data, **kwargs):
		if data.password is None or data.password == 'none':
			await self.instance.gbx.execute('SetServerPasswordForSpectator', '')
			message = '$z$s$fff» $ff0You removed the spectator password.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
		else:
			await self.instance.gbx.execute('SetServerPasswordForSpectator', data.password)
			message = '$z$s$fff» $ff0You changed the spectator password to: "$fff{}$ff0".'.format(data.password)
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
