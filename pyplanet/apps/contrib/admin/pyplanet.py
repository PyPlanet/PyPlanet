"""
Player Admin methods and functions.
"""
import os

from pyplanet.contrib.command import Command


class PyPlanetAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('reboot', 'Reboot PyPlanet pool instance', app=self.app, min_level=3)

		await self.instance.command_manager.register(
			Command(command='reboot', target=self.reboot_pool, perms='admin:reboot', admin=True, description='Reboots PyPlanet.'),
		)

	async def reboot_pool(self, player, data, **kwargs):
		if os.name == 'nt':
			os._exit(50)
			os.execl(sys.executable, sys.executable, *sys.argv)
		else:
			exit(50)
		
