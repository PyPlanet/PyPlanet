"""
Dev app component.
"""
import json

from pyplanet.contrib.command import Command

from .views.call import CallMenuView


class DevComponent:
	def __init__(self, app):
		"""
		Developer tools component

		:param app: App config instance
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		"""
		self.app = app

	async def on_init(self):
		pass

	async def on_start(self):
		await self.app.instance.permission_manager.register(
			'execute_calls', 'Can execute calls to server.', app=self.app, min_level=3
		)

		await self.app.instance.command_manager.register(
			Command('call', self.admin_call, perms='core.pyplanet:execute_calls', admin=True,
					description='Allows execution of API calls on the dedicated server.')
				.add_param('search', type=str, required=False)
		)

	async def admin_call(self, player, data, **kwargs):
		await self.app.instance.chat('$ff0Please wait... loading methods...', player)

		view = CallMenuView(self.app, player)
		if 'search' in data:
			view.search_text = data.search
		await view.display()
		return
