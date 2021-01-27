from pyplanet.contrib.command import Command
from pyplanet.apps.contrib.admin.views.matchsettingsbrowser import MatchSettingsBrowserView


class MatchSettingsBrowser:
	def __init__(self, app):
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register(
			'loadms', 'Shows a file browser to browse the local matchsettings files.',
			app=self.app, min_level=3
		)

		await self.app.instance.command_manager.register(
			Command(command='loadms', target=self.show_browser, perms='admin:loadms', admin=True,
					description='Shows a file browser to browse the local matchsettings files.')
		)

	async def show_browser(self, player, data, **kwargs):
		view = MatchSettingsBrowserView(self.app, player)
		await view.set_dir('')
