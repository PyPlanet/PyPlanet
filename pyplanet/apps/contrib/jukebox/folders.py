from playhouse.shortcuts import model_to_dict

from pyplanet.views.generics.list import ManualListView
from pyplanet.apps.contrib.jukebox.views import MapListView
from pyplanet.utils import times


class JukeboxFolders:
	app = None
	folders = []

	def __init__(self, app):
		self.app = app

		self.folders.append({'id': 'length_shorter_30s', 'name': 'Maps shorter than 30 seconds'})
		self.folders.append({'id': 'length_longer_60s', 'name': 'Maps longer than 60 seconds'})
		#self.folders.append({'id': 'karma_none', 'name': 'Maps with no karma votes'})
		#self.folders.append({'id': 'karma_negative', 'name': 'Maps with a negative karma'})

	async def display_all(self, player):
		view = FoldersListView(self)
		await view.display(player=player)

	async def display_folder(self, player, folder):
		map_list = []
		fields = []

		if folder['id'] is 'length_shorter_30s':
			map_list = [m for m in self.app.instance.map_manager.maps if m.time_author < 30000]
		elif folder['id'] is 'length_longer_60s':
			map_list = [m for m in self.app.instance.map_manager.maps if m.time_author > 60000]

		if folder['id'].startswith('length_'):
			fields.append({
				'name': 'Author time',
				'index': 'time_author',
				'sorting': True,
				'searching': False,
				'width': 25,
			})

		view = ManualMapListView(self.app, map_list, fields)
		view.title = 'Folder: ' + folder['name']
		await view.display(player=player)


class ManualMapListView(MapListView):
	app = None

	def __init__(self, app, map_list, fields):
		super().__init__(app)
		self.app = app
		self.manager = app.context.ui
		self.map_list = map_list
		self.fields = fields

	async def get_fields(self):
		fields = await super().get_fields()

		for field in self.fields:
			fields.append(field)

		return fields

	async def get_data(self):
		items = []
		for item in self.map_list:
			dict_item = model_to_dict(item)
			dict_item['time_author'] = times.format_time(dict_item['time_author'])
			items.append(dict_item)

		return items


class FoldersListView(ManualListView):
	app = None
	folders = None

	title = 'Maplist folders'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	data = []

	def __init__(self, folders):
		super().__init__(self)
		self.folders = folders
		self.app = folders.app
		self.manager = folders.app.context.ui

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
				'name': 'Folder name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 50,
				'type': 'label',
				'action': self.action_show
			},
		]

	async def action_show(self, player, values, instance, **kwargs):
		await self.folders.display_folder(player, instance)

	async def get_data(self):
		index = 1
		items = []
		for item in self.folders.folders:
			items.append({'index': index, 'id': item['id'], 'name': item['name']})
			index += 1

		return items
