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

		await self.instance.command_manager.register(
			Command(command='setpassword', target=self.set_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='srvpass', target=self.set_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='setspecpassword', target=self.set_spec_password, perms='admin:password', admin=True).add_param(name='password', required=False),
			Command(command='spectpass', target=self.set_spec_password, perms='admin:password', admin=True).add_param(name='password', required=False)
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
