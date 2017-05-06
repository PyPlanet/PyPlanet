"""
Player Admin methods and functions.
"""
from pyplanet.contrib.command import Command
from pyplanet.contrib.player.exceptions import PlayerNotFound


class PlayerAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('ignore', 'Ignore a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('unignore', 'Unignore a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('kick', 'Kick a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('ban', 'Ban a player', app=self.app, min_level=2)
		await self.instance.permission_manager.register('unban', 'Unban a player', app=self.app, min_level=2)

		await self.instance.command_manager.register(
			Command(command='mute', aliases=['ignore'], target=self.ignore_player, perms='admin:ignore', admin=True).add_param(name='login', required=True),
			Command(command='unmute', aliases=['unignore'], target=self.unignore_player, perms='admin:unignore', admin=True).add_param(name='login', required=True),
			Command(command='kick', target=self.kick_player, perms='admin:kick', admin=True).add_param(name='login', required=True),
			Command(command='ban', target=self.ban_player, perms='admin:ban', admin=True).add_param(name='login', required=True),
			Command(command='unban', target=self.unban_player, perms='admin:unban', admin=True).add_param(name='login', required=True),
		)

	async def ignore_player(self, player, data, **kwargs):
		try:
			mute_player = await self.instance.player_manager.get_player(data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has muted $fff{}$z$s$ff0.'.format(player.nickname, mute_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('Ignore', data.login),
				self.instance.gbx.prepare('ChatSendServerMessage', message)
			)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def unignore_player(self, player, data, **kwargs):
		try:
			unmute_player = await self.instance.player_manager.get_player(data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has un-muted $fff{}$z$s$ff0.'.format(player.nickname, unmute_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('UnIgnore', data.login),
				self.instance.gbx.prepare('ChatSendServerMessage', message)
			)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def kick_player(self, player, data, **kwargs):
		try:
			kick_player = await self.instance.player_manager.get_player(data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has kicked $fff{}$z$s$ff0.'.format(player.nickname, kick_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('Kick', data.login),
				self.instance.gbx.prepare('ChatSendServerMessage', message)
			)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def ban_player(self, player, data, **kwargs):
		try:
			ban_player = await self.instance.player_manager.get_player(data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has banned $fff{}$z$s$ff0.'.format(player.nickname, ban_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('Ban', data.login),
				self.instance.gbx.prepare('ChatSendServerMessage', message)
			)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def unban_player(self, player, data, **kwargs):
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has un-banned $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx.prepare('UnBan', data.login),
			self.instance.gbx.prepare('ChatSendServerMessage', message)
		)

	async def blacklist_player(self, player, data, **kwargs):
		try:
			blacklist_player = await self.instance.player_manager.get_player(data.login)
			message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has blacklisted $fff{}$z$s$ff0.'.format(player.nickname, blacklist_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('BlackList', data.login),
				self.instance.gbx.prepare('Kick', data.login),
				self.instance.gbx.prepare('ChatSendServerMessage', message)
			)
		except PlayerNotFound:
			message = '$z$s$fff» $i$f00Unknown login!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def unblacklist_player(self, player, data, **kwargs):
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has un-blacklisted $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx.prepare('UnBlackList', data.login),
			self.instance.gbx.prepare('ChatSendServerMessage', message)
		)
