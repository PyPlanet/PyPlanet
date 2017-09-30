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
				self.folders.append({'id': 'local_none', 'name': 'Map record: none', 'owner': 'PyPlanet'})
				self.folders.append({'id': 'length_shorter_30s', 'name': 'Map record: below 30 seconds', 'owner': 'PyPlanet'})
				self.folders.append({'id': 'length_longer_60s', 'name': 'Map record: above 60 seconds', 'owner': 'PyPlanet'})

			if 'karma' in self.app.instance.apps.apps:
				self.folders.append({'id': 'karma_none', 'name': 'Map karma: no votes', 'owner': 'PyPlanet'})
				self.folders.append({'id': 'karma_negative', 'name': 'Map karma: negative', 'owner': 'PyPlanet'})
				self.folders.append({'id': 'karma_positive', 'name': 'Map karma: positive', 'owner': 'PyPlanet'})

		view = FoldersListView(self)
		await view.display(player=player)

	async def display_folder(self, player, folder):
		map_list = []
		fields = []

		if folder['id'] is 'local_none':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'local') and m.local['record_count'] == 0]
		elif folder['id'] is 'length_shorter_30s':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'local') and m.local['first_record'] is not None and m.local['first_record'].score < 30000]
		elif folder['id'] is 'length_longer_60s':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'local') and m.local['first_record'] is not None and m.local['first_record'].score > 60000]
		elif folder['id'] is 'karma_none':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['vote_count'] is 0]
		elif folder['id'] is 'karma_negative':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['map_karma'] < 0]
		elif folder['id'] is 'karma_positive':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['map_karma'] > 0]

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
				dict_item['local_record'] = times.format_time((item.local['first_record'].score if hasattr(item, 'local') else 0))
			if karma:
				dict_item['karma'] = item.karma['map_karma'] if hasattr(item, 'karma') else 0
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
				'name': 'Folder',
				'index': 'name',
				'sorting': False,
				'searching': True,
				'width': 140,
				'type': 'label',
				'action': self.action_show
			},
			{
				'name': 'Owner',
				'index': 'owner',
				'sorting': False,
				'searching': False,
				'width': 80,
			},
		]

	async def action_show(self, player, values, instance, **kwargs):
		await self.folders.display_folder(player, instance)

	async def get_data(self):
		return self.folders.folders
