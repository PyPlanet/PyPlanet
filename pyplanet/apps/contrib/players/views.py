from playhouse.shortcuts import model_to_dict

from pyplanet.apps.core.maniaplanet.models import Player

from pyplanet.views.generics.list import ManualListView


class PlayerListView(ManualListView):
	model = Player
	title = 'Players currently on this server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui

	async def get_data(self):
		return [{'nickname': m.nickname, 'login': m.login, 'is_spectator': 'Yes' if m.flow.is_spectator else 'No'} for m in self.app.instance.player_manager.online]

	async def get_fields(self):
		return [
			{
				'name': 'Nickname',
				'index': 'nickname',
				'sorting': True,
				'searching': True,
				'width': 100,
				'type': 'label'
			},
			{
				'name': 'Login',
				'index': 'login',
				'sorting': True,
				'searching': True,
				'width': 50,
				'type': 'label'
			},
			{
				'name': 'Is spectator',
				'index': 'is_spectator',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
		]
