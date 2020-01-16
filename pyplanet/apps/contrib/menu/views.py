from pyplanet.views.generics.widget import TemplateView


class MenuView(TemplateView):
	template_name = 'menu/menu.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(app.context.ui, *args, **kwargs)
		self.app = app
		self.manager = app.context.ui
		self.id = 'menu'
		self.subscribe('vote_skip', self.action_vote_skip)
		self.subscribe('vote_restart', self.action_vote_restart)
		self.subscribe('vote_extend', self.action_vote_extend)
		self.subscribe('vote_adm_cancel', self.action_vote_adm_cancel)
		self.subscribe('vote_adm_pass', self.action_vote_adm_pass)

		self.subscribe('players', self.action_players)
		self.subscribe('maps', self.action_maps)

		self.subscribe('adm_prev', self.action_adm_prev)
		self.subscribe('adm_res', self.action_adm_res)
		self.subscribe('adm_skip', self.action_adm_skip)
		self.subscribe('adm_replay', self.action_adm_replay)
		self.subscribe('adm_er', self.action_adm_er)
		self.subscribe('adm_shuffle', self.action_adm_shuffle)

		self.subscribe('adm_server', self.action_adm_server)
		self.subscribe('adm_mode', self.action_adm_mode)
		self.subscribe('adm_settings', self.action_adm_settings)
		self.subscribe('adm_players', self.action_adm_players)

	async def get_context_data(self):
		context = await super().get_context_data()
		context['player_level'] = 0
		return context

	async def get_per_player_data(self, login):
		data = await super().get_per_player_data(login)
		data['player_level'] = 0
		player = await self.app.instance.player_manager.get_player(login)
		if player:
			data['player_level'] = player.level
		return data

	async def action_vote_skip(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/skip')

	async def action_vote_restart(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/res')

	async def action_vote_extend(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/extend')

	async def action_vote_adm_cancel(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//cancel')

	async def action_vote_adm_pass(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//pass')

	async def action_maps(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/list')

	async def action_players(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/players')

	async def action_adm_skip(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//skip')

	async def action_adm_res(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//res')

	async def action_adm_prev(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//prev')

	async def action_adm_replay(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//replay')

	async def action_adm_er(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//endround')

	async def action_adm_server(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//server')

	async def action_adm_mode(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//modesettings')

	async def action_adm_settings(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//settings')

	async def action_adm_players(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//players')

	async def action_adm_shuffle(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//shuffle')
