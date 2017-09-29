from playhouse.shortcuts import model_to_dict

from pyplanet.views.generics.list import ManualListView
from pyplanet.apps.contrib.jukebox.views import MapListView
from pyplanet.utils import times


class JukeboxFolders:
	app = None
	folders = []

	def __init__(self, app):
		self.app = app

	async def display_all(self, player):
		if len(self.folders) == 0:
			if 'local_records' in self.app.instance.apps.apps:
				self.folders.append({'id': 'length_shorter_30s', 'name': 'Maps shorter than 30 seconds (based on Local Record)'})
				self.folders.append({'id': 'length_longer_60s', 'name': 'Maps longer than 60 seconds (based on Local Record)'})

			if 'karma' in self.app.instance.apps.apps:
				self.folders.append({'id': 'karma_none', 'name': 'Maps with no karma votes'})
				self.folders.append({'id': 'karma_negative', 'name': 'Maps with a negative karma'})
				self.folders.append({'id': 'karma_positive', 'name': 'Maps with a positive karma'})

		view = FoldersListView(self)
		await view.display(player=player)

	async def display_folder(self, player, folder):
		map_list = []
		fields = []

		if folder['id'] is 'length_shorter_30s':
			map_list = [m for m in self.app.instance.map_manager.maps if (await self.app.instance.apps.apps['local_records'].get_map_record(self, m))['first_record'] < 30000]
		elif folder['id'] is 'length_longer_60s':
			map_list = [m for m in self.app.instance.map_manager.maps if (await self.app.instance.apps.apps['local_records'].get_map_record(self, m))['first_record'] > 60000]
		elif folder['id'] is 'karma_none':
			map_list = [m for m in self.app.instance.map_manager.maps if await self.app.instance.apps.apps['karma'].get_map_vote_count(self, m) is 0]
		elif folder['id'] is 'karma_negative':
			map_list = [m for m in self.app.instance.map_manager.maps if await self.app.instance.apps.apps['karma'].get_map_karma(self, m) < 0]
		elif folder['id'] is 'karma_positive':
			map_list = [m for m in self.app.instance.map_manager.maps if await self.app.instance.apps.apps['karma'].get_map_karma(self, m) > 0]

		if folder['id'].startswith('length_'):
			fields.append({
				'name': 'Local Record',
				'index': 'local_record',
				'sorting': True,
				'searching': False,
				'width': 40,
			})

		if folder['id'].startswith('karma_'):
			fields.append({
				'name': 'Karma',
				'index': 'karma',
				'sorting': True,
				'searching': False,
				'width': 40,
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
		karma = any(f['index'] == "karma" for f in self.fields)
		length = any(f['index'] == "local_record" for f in self.fields)

		items = []
		for item in self.map_list:
			dict_item = model_to_dict(item)
			if length:
				dict_item['local_record'] = times.format_time((await self.app.instance.apps.apps['local_records'].get_map_record(self, item))['first_record'])
			if karma:
				dict_item['karma'] = await self.app.instance.apps.apps['karma'].get_map_karma(self, item)
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
				'width': 100,
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
