from pyplanet.views import TemplateView


class ToolbarView(TemplateView):
	template_name = 'core.pyplanet/toolbar.xml'

	def __init__(self, app, *args, **kwargs):
		"""
		Initiate Player Toolbar

		:param app: App instance.
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		"""
		super().__init__(*args, **kwargs)

		self.id = 'pyplanet__toolbar'
		self.app = app
		self.manager = self.app.context.ui

		self.commands = {
			'bar_button_list': '/list',
			'bar_button_mf': '/mf',
			'bar_button_jb': '/jukebox list',
			'bar_button_skip': '/skip',
			'bar_button_extend': '/extend',
			'bar_button_replay': '/replay',
			'bar_button_players': '/players',
			'bar_button_topdons': '/topdons',
			'bar_button_topsums': '/topsums',
			'bar_button_topactive': '/topactive',
			'bar_button_mxinfo': '/{} info'.format('tmx' if self.app.instance.game.game == 'tmnext' else 'mx'),
			'bar_button_help': '/helpall',
		}

	async def get_context_data(self):
		data = await super().get_context_data()
		data['game'] = self.app.instance.game.game
		return data

	async def handle_catch_all(self, player, action, values, **kwargs):
		if action not in self.commands:
			return
		await self.app.instance.command_manager.execute(player, self.commands[action])
