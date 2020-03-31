from pyplanet.contrib.command import Command
from pyplanet.apps.contrib.admin.views.mapbrowser import BrowserView


class MapBrowser:
	def __init__(self, app):
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register(
			'localmaps', 'Shows a file browser to browse the local files',
			app=self.app, min_level=3
		)

		await self.app.instance.command_manager.register(
			Command(command='localmaps', target=self.show_browser, perms='admin:localmaps', admin=True,
					description='Shows a file browser to browse local files.')
		)

	async def show_browser(self, player, data, **kwargs):
		view = BrowserView(self.app, player)
		await view.set_dir('')
