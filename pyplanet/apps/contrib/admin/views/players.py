"""
Mode Settings Views.
"""

from pyplanet.views.generics import ManualListView


class PlayerListView(ManualListView):
	title = 'Players'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	def __init__(self, app, player):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.contrib.admin.Admin
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		super().__init__()
		self.manager = app.context.ui
		self.app = app
		self.player = player
		self.fields = [
			{
				'name': 'Nickname',
				'index': 'nickname',
				'sorting': True,
				'searching': True,
				'width': 60,
				'type': 'label'
			},
			{
				'name': 'Login',
				'index': 'login',
				'input': True,
				'sorting': False,
				'searching': True,
				'width': 40,
				'type': 'label',
			},
			{
				'name': 'Spec',
				'index': 'is_spectator',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label',
				'safe': True
			},
			{
				'name': 'Level',
				'index': 'level',
				'sorting': True,
				'searching': False,
				'width': 35,
				'type': 'label'
			},
		]
		self.sort_field = self.fields[2]

		self.child = None

	async def get_data(self):
		players = self.app.instance.player_manager.online
		return [dict(
			nickname=p.nickname,
			login='{}'.format(p.login),
			is_spectator='$f00&#xf03d;' if p.flow.is_spectator else '$73f&#xf007;',
			is_spectator_bool=p.flow.is_spectator,
			level='{}: {}'.format(p.level, p.get_level_string())
		) for p in players]

	async def display(self, **kwargs):
		kwargs['player'] = self.player
		return await super().display(**kwargs)

	async def get_actions(self):
		return [
			{
				'name': 'Force spec/player',
				'type': 'label',
				'text': 'Force',
				'width': 12,
				'action': self.action_force,
				'safe': True,
			},
			{
				'name': 'Ignore',
				'type': 'label',
				'text': 'Ignore',
				'width': 12,
				'action': self.action_ignore,
				'safe': True,
			},
			{
				'name': 'Warn',
				'type': 'label',
				'text': 'Warn',
				'width': 12,
				'action': self.action_warn,
				'safe': True,
			},
			{
				'name': 'Kick',
				'type': 'label',
				'text': 'Kick',
				'width': 12,
				'action': self.action_kick,
				'safe': True,
			},
			{
				'name': 'Ban',
				'type': 'label',
				'text': 'Ban',
				'width': 12,
				'action': self.action_ban,
				'safe': True,
			},
			{
				'name': 'Blacklist',
				'type': 'label',
				'text': 'Blacklist',
				'width': 12,
				'action': self.action_blacklist,
				'safe': True,
			},
		]

	async def action_force(self, user, values, player, *args, **kwargs):
		if player['is_spectator_bool']:
			await self.app.instance.command_manager.execute(user, '//forceplay', player['login'])
		else:
			await self.app.instance.command_manager.execute(user, '//forcespec', player['login'])
		await self.refresh(self.player)

	async def action_ignore(self, user, values, player, *args, **kwargs):
		ignore_list = await self.app.instance.gbx('GetIgnoreList', -1, 0)
		in_list = False
		for entry in ignore_list:
			if entry and entry['Login'] == player['login']:
				in_list = True
				break

		if not in_list:
			await self.app.instance.command_manager.execute(user, '//ignore', player['login'])
		else:
			await self.app.instance.command_manager.execute(user, '//unignore', player['login'])
		await self.refresh(self.player)

	async def action_warn(self, user, values, player, *args, **kwargs):
		await self.app.instance.command_manager.execute(user, '//warn', player['login'])

	async def action_kick(self, user, values, player, *args, **kwargs):
		await self.app.instance.command_manager.execute(user, '//kick', player['login'])
		await self.refresh(self.player)

	async def action_ban(self, user, values, player, *args, **kwargs):
		await self.app.instance.command_manager.execute(user, '//ban', player['login'])
		await self.refresh(self.player)

	async def action_blacklist(self, user, values, player, *args, **kwargs):
		await self.app.instance.command_manager.execute(user, '//blacklist', player['login'])
		await self.refresh(self.player)
