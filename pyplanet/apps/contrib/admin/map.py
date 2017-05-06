"""
Map Admin methods and functions.
"""
from pyplanet.contrib.command import Command


class MapAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('next', 'Skip to the next map', app=self.app, min_level=1)
		await self.instance.permission_manager.register('restart', 'Restart the maps', app=self.app, min_level=1)

		await self.instance.command_manager.register(
			Command(command='next', target=self.next_map, perms='admin:next', admin=True),
			Command(command='skip', target=self.next_map, perms='admin:next', admin=True),
			Command(command='restart', aliases=['res', 'rs'], target=self.restart_map, perms='admin:restart', admin=True),
		)

	async def next_map(self, player, data, **kwargs):
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has skipped to the next map.'.format(player.nickname)
		await self.instance.gbx.multicall(
			self.instance.gbx.prepare('NextMap'),
			self.instance.gbx.prepare('ChatSendServerMessage', message)
		)

	async def restart_map(self, player, data, **kwargs):
		message = '$z$s$fff»» $ff0Admin $fff{}$z$s$ff0 has restarted the map.'.format(player.nickname)
		await self.instance.gbx.multicall(
			self.instance.gbx.prepare('RestartMap'),
			self.instance.gbx.prepare('ChatSendServerMessage', message)
		)

