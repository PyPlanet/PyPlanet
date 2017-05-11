"""
Server Admin methods and functions.
"""
from pyplanet.contrib.command import Command


class ServerAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('password', 'Set the server passwords', app=self.app, min_level=2)
		await self.instance.permission_manager.register('servername', 'Set the server name', app=self.app, min_level=2)
		await self.instance.permission_manager.register('mode', 'Set the server game mode', app=self.app, min_level=2)

		await self.instance.command_manager.register(
			Command(command='setpassword', aliases=['srvpass'], target=self.set_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='setspecpassword', aliases=['spectpass'], target=self.set_spec_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='servername', target=self.set_servername, perms='admin:servername', admin=True).add_param(name='server_name', required=True, nargs='*'),
			Command(command='mode', target=self.set_mode, perms='admin:mode', admin=True).add_param(name='mode', required=True, nargs='*')
		)

	async def set_mode(self, player, data, **kwargs):
		mode = ' '.join(data.mode)

		if mode == 'ta':
			mode = 'TimeAttack.Script.txt'
		elif mode == 'laps':
			mode = 'Laps.Script.txt'
		elif mode == 'rounds':
			mode = 'Rounds.Script.txt'
		elif mode == 'cup':
			mode = 'Cup.Script.txt'
		elif mode == 'chase':
			mode = 'Chase.Script.txt'

		try:
			await self.instance.mode_manager.set_next_script(mode)
		except Exception as e:
			message = '$z$s$fff» $ff0Mode change failed: {}'.format(str(e))
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			return
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has changed the next mode to {}'.format(
			player.nickname, mode
		)
		await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def set_servername(self, player, data, **kwargs):
		name = ' '.join(data.server_name)
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has changed the server name into {}'.format(
			player.nickname, name
		)
		await self.instance.gbx.multicall(
			self.instance.gbx.prepare('SetServerName', name),
			self.instance.gbx.prepare('ChatSendServerMessage', message)
		)

	async def set_spec_password(self, player, data, **kwargs):
		if data.password is None or data.password == 'none':
			message = '$z$s$fff» $ff0You removed the spectator password.'
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('SetServerPasswordForSpectator', ''),
				self.instance.gbx.prepare('ChatSendServerMessageToLogin', message, player.login)
			)
		else:
			message = '$z$s$fff» $ff0You changed the spectator password to: "$fff{}$ff0".'.format(data.password)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('SetServerPasswordForSpectator', data.password),
				self.instance.gbx.prepare('ChatSendServerMessageToLogin', message, player.login)
			)

	async def set_password(self, player, data, **kwargs):
		if data.password is None or data.password == 'none':
			message = '$z$s$fff» $ff0You removed the server password.'
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('SetServerPassword', ''),
				self.instance.gbx.prepare('ChatSendServerMessageToLogin', message, player.login)
			)
		else:
			message = '$z$s$fff» $ff0You changed the server password to: "$fff{}$ff0".'.format(data.password)
			await self.instance.gbx.multicall(
				self.instance.gbx.prepare('SetServerPassword', data.password),
				self.instance.gbx.prepare('ChatSendServerMessageToLogin', message, player.login)
			)
