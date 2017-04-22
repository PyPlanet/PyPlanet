from pyplanet.apps.core.maniaplanet.models import Map

from pyplanet.views.generics.list import ListView


class MapListView(ListView):
	app = None

	model = Map
	query = Map.select()
	title = 'Map List Testing'
	icon_style = 'Icons64x64_1'
	icon_substyle = 'Browser'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.ui

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
				row.author_nickname if row.author_nickname and len(row.author_nickname) > 0 else row.author_login,
				'width': 50,
				'action': lambda player, values, instance:
				print(player, values, instance)
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

	async def action_jukebox(self, player, values, instance, **kwargs):
		await self.app.add_to_jukebox(player, instance)

	async def action_delete(self, player, values, instance, **kwargs):
		print('Delete value: {}'.format(instance))
