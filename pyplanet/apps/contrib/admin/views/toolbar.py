"""
Toolbar View.
"""

from pyplanet.views import TemplateView


class ToolbarView(TemplateView):
	"""
	Toolbar View Class.
	"""
	template_name = 'admin/toolbar/toolbar.xml'

	def __init__(self, app):
		"""
		Initiate the toolbar view.

		:param app: Admin app instance.
		:type app: pyplanet.apps.contrib.admin.Admin
		"""
		super().__init__(app.context.ui)

		self.app = app
		self.id = 'admin_toolbar'

		self.subscribe('bar_button_prev', self.action_prev)
		self.subscribe('bar_button_endround', self.action_endround)
		self.subscribe('bar_button_restart', self.action_restart)
		self.subscribe('bar_button_replay', self.action_replay)
		self.subscribe('bar_button_skip', self.action_skip)

		self.subscribe('bar_button_settings', self.action_settings)
		self.subscribe('bar_button_modesettings', self.action_modesettings)
		self.subscribe('bar_button_players', self.action_player_list)

	async def get_context_data(self):
		data = await super().get_context_data()
		data['game'] = self.app.instance.game.game
		return data

	async def action_prev(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//prev')

	async def action_endround(self, player, *args, **kwargs):
		if self.app.instance.game.game == 'sm':
			return await self.app.instance.chat('$ff0Error: Can\'t end round in Shootmania!', player)
		return await self.app.instance.command_manager.execute(player, '//endround')

	async def action_replay(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//replay')

	async def action_skip(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//skip')

	async def action_settings(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//settings')

	async def action_modesettings(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//modesettings')

	async def action_player_list(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//players')

	async def action_restart(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//restart')
