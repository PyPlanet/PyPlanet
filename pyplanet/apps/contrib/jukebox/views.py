from playhouse.shortcuts import model_to_dict

from pyplanet.apps.core.maniaplanet.models import Map

from pyplanet.views.generics.list import ListView, ManualListView


class JukeboxListView(ManualListView):
	app = None

	title = 'Currently in the Jukebox'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	data = []

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': True,
				'searching': False,
				'width': 10,
				'type': 'label'
			},
			{
				'name': 'Map',
				'index': 'map_name',
				'sorting': True,
				'searching': True,
				'width': 100,
				'type': 'label',
				'action': self.action_drop
			},
			{
				'name': 'Requested by',
				'index': 'player_nickname',
				'sorting': True,
				'searching': False,
				'width': 50
			},
		]

	async def action_drop(self, player, values, instance, **kwargs):
		await self.app.drop_from_jukebox(player, instance)


class MapListView(ManualListView):
	model = Map
	title = 'Maps on this server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui

	async def get_data(self):
		return [model_to_dict(m) for m in self.app.instance.map_manager.maps]

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 100,
				'type': 'label',
				'action': self.action_jukebox
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'renderer': lambda row, field:
					row['author_nickname']
					if 'author_nickname' in row and row['author_nickname'] and len(row['author_nickname'])
					else row['author_login'],
				'width': 50,
			},
		]

	async def get_actions(self):
		return [
			{
				'name': 'Delete',
				'action': self.action_delete,
				'style': 'Icons64x64_1',
				'substyle': 'Close'
			}
		]

	async def action_jukebox(self, player, values, map_info, **kwargs):
		await self.app.add_to_jukebox(player, await self.app.instance.map_manager.get_map(map_info['uid']))

	async def action_delete(self, player, values, map_info, **kwargs):
		print('Delete value: {}'.format(map_info))
