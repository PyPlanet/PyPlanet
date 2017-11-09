import asyncio

from playhouse.shortcuts import model_to_dict

from pyplanet.apps.contrib.jukebox.models import MapFolder, MapInFolder
from pyplanet.apps.core.maniaplanet.models import Map
from pyplanet.views import TemplateView
from pyplanet.views.generics.alert import show_alert, ask_confirmation
from pyplanet.views.generics.list import ManualListView

from pyplanet.utils import times


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

	async def get_data(self):
		index = 1
		items = []
		for item in self.app.jukebox:
			items.append({'index': index, 'map_name': item['map'].name, 'player_nickname': item['player'].nickname,
						  'player_login': item['player'].login})
			index += 1

		return items


class MapListView(ManualListView):
	model = Map
	title = 'Maps on this server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	custom_actions = list()

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
				'search_strip_styles': True,
				'width': 90,
				'type': 'label',
				'action': self.action_jukebox
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'renderer': lambda row, field:
				row['author_login'],
				# TODO: Activate after resolving #83.
				# row['author_nickname']
				# if 'author_nickname' in row and row['author_nickname'] and len(row['author_nickname'])
				# else row['author_login'],
				'width': 50,
			},
		]

	async def get_actions(self):
		return self.custom_actions

	async def get_buttons(self):
		return [
			{
				'title': 'Folders',
				'width': 20,
				'action': self.action_folders
			}
		]

	async def action_jukebox(self, player, values, map_info, **kwargs):
		await self.app.add_to_jukebox(player, await self.app.instance.map_manager.get_map(map_info['uid']))

	async def action_folders(self, player, values, **kwargs):
		await self.app.folder_manager.display_folder_list(player)

	@classmethod
	def add_action(cls, target, name, text, text_size='1.2', require_confirm=False, order=0):
		cls.custom_actions.append(dict(
			name=name,
			action=target,
			text=text,
			textsize=text_size,
			safe=True,
			type='label',
			order=order,
			require_confirm=require_confirm,
		))

		cls.custom_actions = sorted(cls.custom_actions, key=lambda k: k['order'])

	@classmethod
	def remove_action(cls, target):
		for idx, custom in enumerate(cls.custom_actions):
			if custom['action'] == target:
				del cls.custom_actions[idx]


class FolderMapListView(MapListView):
	def __init__(self, folder_manager, folder_code, player):
		"""
		Folder Map list

		:param folder_manager: Folder manager
		:param folder_code: Folder code that can be parsed.
		:type folder_manager: pyplanet.apps.contrib.jukebox.folders.FolderManager
		"""
		super().__init__(folder_manager.app)

		self.folder_manager = folder_manager
		self.folder_code = folder_code
		self.player = player

		self.map_list = list()
		self.folder_info = None
		self.folder_instance = None

	async def get_fields(self):
		fields = await super().get_fields()

		for field in self.fields:
			fields.append(field)

		return fields

	async def get_data(self):
		self.fields, self.map_list, self.folder_info, self.folder_instance = \
			await self.folder_manager.get_folder_code_contents(self.folder_code)

		self.title = 'Folder: ' + self.folder_info['name']

		karma = any(f['index'] == "karma" for f in self.fields)
		length = any(f['index'] == "local_record" for f in self.fields)

		items = []
		for item in self.map_list:
			dict_item = model_to_dict(item)
			if length:
				dict_item['local_record'] = times.format_time((item.local['first_record'].score if hasattr(item, 'local') and item.local['first_record'] else 0))
			if karma:
				dict_item['karma'] = item.karma['map_karma'] if hasattr(item, 'karma') else 0
			items.append(dict_item)

		return items

	async def remove_from_folder(self, player, values, map_dictionary, view, **kwargs):
		# Check permission on folder.
		if (self.folder_instance.public and player.level < player.LEVEL_ADMIN)\
			or (not self.folder_instance.public and self.folder_instance.player_id != player.id):
			await show_alert(player, 'You are not allowed to remove the map from the folder!', size='sm')
			return

		# Ask for confirmation.
		cancel = bool(await ask_confirmation(player, 'Are you sure you want to remove the map \'{}\'$z$s from the folder?'.format(
			map_dictionary['name']
		), size='sm'))
		if cancel is True:
			return

		# Remove from folder.
		await MapInFolder.execute(
			MapInFolder.delete()
				.where((MapInFolder.map_id == map_dictionary['id']) & (MapInFolder.folder_id == self.folder_instance.id))
		)

		# Refresh list.
		await self.refresh(player)

	async def get_buttons(self):
		buttons = await super().get_buttons()

		if (self.folder_code['type'] == 'public' and self.player.level >= self.player.LEVEL_ADMIN) \
			or (self.folder_code['type'] == 'public' and self.folder_code['owner_login'] == self.player.login) \
			or (self.folder_code['type'] == 'private' and self.folder_code['owner_login'] == self.player.login):
			buttons.append({
				'title': 'Add current map',
				'width': 38,
				'action': self.action_add_current
			})

		return buttons

	async def get_actions(self):
		super_actions = (await super().get_actions()).copy()

		# If this folder is not a dynamic one, add remove button.
		if self.folder_instance:
			super_actions.append(dict(
				name='Remove from folder',
				action=self.remove_from_folder,
				text='&#xf056;',
				textsize='1.2',
				safe=True,
				type='label',
				order=49,
				require_confirm=False,
			))

		return sorted(super_actions, key=lambda k: k['order'])

	async def action_add_current(self, player, values, **kwargs):
		if self.app.instance.map_manager.current_map.id in [m.id for m in self.map_list]:
			await show_alert(player, 'The current map is already in this folder!', 'sm')
			return

		# Add map to folder.
		map_in_folder = MapInFolder(
			map_id=self.app.instance.map_manager.current_map.id,
			folder=self.folder_instance
		)
		await map_in_folder.save()

		await show_alert(player, 'Map has been added to the folder!', 'sm')
		await self.display(player)


class FolderListView(ManualListView):
	title = 'Maplist folders'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	def __init__(self, folder_manager, player):
		super().__init__()

		self.folder_manager = folder_manager
		self.player = player
		self.app = folder_manager.app
		self.manager = folder_manager.app.context.ui

		self.child = None

	@staticmethod
	def render_folder_name(row, field):
		icon = ''
		if row['type'] == 'auto':
			icon = '\uf013'
		elif row['type'] == 'public':
			icon = '\uf0c0'
		elif row['type'] == 'private':
			icon = '\uf023'

		return '{} {}'.format(icon, row[field['index']])

	async def get_fields(self):
		return [
			{
				'name': 'Folder',
				'index': 'name',
				'sorting': False,
				'searching': True,
				'width': 130,
				'renderer': self.render_folder_name,
				'type': 'label',
				'action': self.action_show
			},
			{
				'name': 'Type',
				'index': 'type',
				'sorting': True,
				'searching': False,
				'width': 30,
				'renderer': lambda row, field:
					row[field['index']].capitalize(),
				'type': 'label'
			},
			{
				'name': 'Owner',
				'index': 'owner',
				'sorting': False,
				'searching': False,
				'width': 80,
			},
		]

	async def get_buttons(self):
		return [
			{
				'title': 'Create folder',
				'width': 28,
				'action': self.create_folder
			}
		]

	async def get_actions(self):
		return [
			dict(
				name='Delete folder',
				action=self.delete_folder,
				text='&#xf1f8;',
				textsize='1.2',
				safe=True,
				type='label',
				order=49,
				require_confirm=False,
			)]

	async def delete_folder(self, player, values, folder_dictionary, view, **kwargs):
		# Check permission on folder.
		if folder_dictionary['type'] == 'auto':
			await show_alert(player, 'You can not remove an auto-folder!', size='sm')
			return

		# Check permission on folder.
		if folder_dictionary['owner_login'] != player.login:
			await show_alert(player, 'You can not remove folders made by others!', size='sm')
			return

		# Ask for confirmation.
		cancel = bool(await ask_confirmation(player, 'Are you sure you want to remove folder \'{}\'$z$s?'.format(
			folder_dictionary['name']
		), size='sm'))
		if cancel is True:
			return

		# Remove maps from folder.
		await MapInFolder.execute(
			MapInFolder.delete()
				.where(MapInFolder.folder == folder_dictionary['id'].replace('database_', ''))
		)

		# Remove folder.
		await MapFolder.execute(
			MapFolder.delete()
				.where(MapFolder.id == folder_dictionary['id'].replace('database_', ''))
		)

		# Refresh list.
		await self.refresh(player)

	async def action_show(self, player, values, instance, **kwargs):
		await self.folder_manager.display_folder(player, instance)

	async def create_folder(self, player, values, **kwargs):
		if self.child:
			return

		self.child = CreateFolderView(self, player, self.folder_manager)
		await self.child.display()
		await self.child.wait_for_response()
		await self.child.destroy()
		await self.display(self.player)  # refresh.
		self.child = None

	async def get_data(self):
		return await self.folder_manager.get_folders(self.player)


class CreateFolderView(TemplateView):
	"""
	View to create new folder.
	"""
	template_name = 'jukebox/folder_create.xml'

	def __init__(self, parent, player, folder_manager):
		"""
		Initiate child create view.

		:param parent: Parent view.
		:param player: Player instance.
		:param folder_manager: Folder manager instance.
		:type parent: pyplanet.view.base.View
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type folder_manager: pyplanet.apps.contrib.jukebox.folders.FolderManager
		"""
		super().__init__(parent.manager)

		self.parent = parent
		self.player = player
		self.folder_manager = folder_manager
		self.app = folder_manager.app

		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_save', self.save)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()
		context['is_admin'] = self.player.level >= self.player.LEVEL_ADMIN
		return context

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])

		self.response_future.set_result(None)
		self.response_future.done()

	async def wait_for_response(self):
		return await self.response_future

	async def save(self, player, action, values, *args, **kwargs):
		"""
		Save action.

		:param player: Player instance
		:param action: Action label
		:param values: Values from manialink
		:param args: *
		:param kwargs: **
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""

		folder_name = values['folder_name']
		folder_privacy = values['folder_privacy']

		if folder_privacy == 'public' and player.level < player.LEVEL_ADMIN:
			folder_privacy = 'private'

		# Check if the user has already created 5 private folders
		current_folders = await self.folder_manager.get_private_folders(player)
		if folder_privacy == 'private' and len(current_folders) >= 5 and player.level < player.LEVEL_ADMIN:
			self.response_future.set_result(None)
			self.response_future.done()
			return await show_alert(player, 'You reached the maximum of 5 private folders!', 'sm')

		# Check if name is valid.
		if len(folder_name) < 3:
			self.response_future.set_result(None)
			self.response_future.done()
			return await show_alert(player, 'The name you gave is not valid. Please provide a name with at least 3 characters.', 'sm')

		# Create folder.
		await self.folder_manager.create_folder(name=folder_name, player=player, public=folder_privacy == 'public')

		# Return response.
		self.response_future.set_result(None)
		self.response_future.done()


class AddToFolderView(TemplateView):
	"""
	Add map to folder view.
	"""
	template_name = 'jukebox/folder_add.xml'

	def __init__(self, app, player, map_id, folder_manager):
		"""
		Initiate child add-to-folder view.

		:param app: App Instance.
		:param player: Player instance.
		:param map_id: Map database ID.
		:param folder_manager: Folder manager instance.
		:type app: pyplanet.apps.contrib.jukebox.Jukebox
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type folder_manager: pyplanet.apps.contrib.jukebox.folders.FolderManager
		"""
		super().__init__(app.context.ui)
		self.app = app
		self.player = player
		self.map_id = map_id
		self.folder_manager = folder_manager

		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()
		context['folders'] = (await self.folder_manager.get_writable_folders(self.player))[:20]
		return context

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])

		self.response_future.set_result(None)
		self.response_future.done()

	async def wait_for_response(self):
		return await self.response_future

	async def handle_catch_all(self, player, action, values, **kwargs):
		# Filter out the folder selection.
		if not action.startswith('folder_select__'):
			return

		# Fetch the folder from the database.
		try:
			folder = await MapFolder.get(id=action[15:])
		except:
			return  # Ignore exceptions here, could be that the folder has been deleted recently.

		# Check permission on folder.
		if folder.public and player.level < player.LEVEL_ADMIN:
			return
		if not folder.public and folder.player_id != player.id:
			return

		# Check for duplicates.
		existing = await MapInFolder.execute(
			MapInFolder.select(MapInFolder)
				.where((MapInFolder.folder == folder) & (MapInFolder.map_id == self.map_id))
		)

		if len(existing) > 0:
			await show_alert(player, 'Map already in folder!', 'sm')
			return

		# Add map to folder.
		map_in_folder = MapInFolder(
			map_id=self.map_id,
			folder=folder
		)
		await map_in_folder.save()

		self.response_future.set_result(True)
		self.response_future.done()
