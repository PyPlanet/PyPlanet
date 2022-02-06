"""
MX List Views.
"""
import asyncio
import logging

from pyplanet.views.generics import ManualListView, ask_confirmation
from pyplanet.views.generics.widget import WidgetView
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
from datetime import datetime
from collections import namedtuple

logger = logging.getLogger(__name__)


class MxSearchListView(ManualListView):
	def __init__(self, app, player, api):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.contrib.mx.app.RealMX
		"""
		super().__init__()
		self.manager = app.context.ui
		self.player = player
		self.app = app
		self.api = api

		self.template_name = 'mx/search.xml'
		self.response_future = asyncio.Future()

		self.cache = None
		self.has_data = False

		self.search_map = None
		self.search_author = None
		self.provide_search = True

		self.fields = [
			{
				'name': 'ID',
				'index': 'mxid',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label'
			},
			{
				'name': 'Map',
				'index': 'gbxname',
				'sorting': True,
				'searching': False,
				'width': 55,
				'type': 'label'
			},
			{
				'name': 'Author',
				'index': 'author',
				'sorting': True,
				'searching': False,
				'width': 40,
				'type': 'label',
			},
			{
				'name': 'Environment',
				'index': 'envir',
				'sorting': False,
				'searching': False,
				'width': 25,
				'type': 'label',
				'safe': True
			},
			{
				'name': 'Awards',
				'index': 'awards',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label'
			},
			{
				'name': 'Difficulty',
				'index': 'difficulty',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
		]

		if self.app.instance.game.game in ['tm', 'tmnext']:
			self.fields.append({
				'name': 'Length',
				'index': 'length',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			})

		self.sort_field = None
		self.child = None
		self.subscribe("mx_search", self.action_search)

	async def get_title(self):
		return '🔍 Search {}'.format(self.app.site_name)

	async def get_data(self):
		if not self.has_data:
			# First opening, request the data.
			await self.do_search(refresh=False)
			self.has_data = True

		return self.cache

	async def get_object_data(self):
		data = await super().get_object_data()
		data['search_map'] = self.search_map
		data['search_author'] = self.search_author
		return data

	async def display(self, player=None):
		return await super().display(player or self.player)

	async def get_actions(self):
		return [
			{
				'name': 'Install map',
				'type': 'label',
				'text': 'Install',
				'width': 12,
				'action': self.action_install,
				'safe': True
			}
		]

	async def action_install(self, user, values, map, *args, **kwargs):
		await self.app.instance.command_manager.execute(
			user,
			'//{} add'.format(self.app.namespace),
			str(map['mxid'])
		)

	async def action_search(self, user, action, values, *args, **kwargs):
		self.search_map = values['map']
		self.search_author = values['author']

		if values['map'] == "Search Map...":
			self.search_map = None
		if values['author'] == "Search Author...":
			self.search_author = None

		await self.do_search(self.search_map, self.search_author)

	async def do_search(self, trackname=None, authorname=None, refresh=True, **terms):
		try:
			options = {
				"api": "on",
				"mode": 0,
				"gv": 1,
				"limit": 100,
				"tpack": self.app.instance.game.dedicated_title.split("@", 1)[0]
			}

			if trackname is not None:
				options['trackname'] = trackname

			if authorname is not None:
				options['anyauthor'] = authorname

			infos = await self.api.search(options)
			if len(infos) == 0:
				raise MXMapNotFound("No results for search")

		except MXMapNotFound as e:
			message = '$f00Error requesting {}-API: Map not found!'.format(self.app.site_short_name)
			await self.app.instance.chat(message, self.player)
			logger.debug('{}-API: Map not found: {}'.format(self.app.site_short_name, str(e)))
			return None
		except MXInvalidResponse as e:
			message = '$f00Error requesting {}-API: Got an invalid response!'.format(self.app.site_short_name)
			await self.app.instance.chat(message, self.player)
			logger.warning('{}-API: Invalid response: {}'.format(self.app.site_short_name, str(e)))
			return None
		if self.app.instance.game.game in ['tm', 'tmnext']:
			self.cache = [dict(
				mxid=_map['TrackID'],
				name=_map['Name'],
				gbxname=_map['GbxMapName'] if _map['GbxMapName'] != '?' else _map['Name'],
				author=_map['Username'],
				envir=_map['EnvironmentName'],
				awards='$fff🏆 {}'.format(_map['AwardCount']) if _map['AwardCount'] > 0 else "",
				length=_map['LengthName'],
				difficulty=_map['DifficultyName'],
				maptype=_map['MapType'],
				style=_map['StyleName']
			) for _map in infos]
		else:
			self.cache = [dict(
				mxid=_map['TrackID'],
				name=_map['Name'],
				gbxname=_map['GbxMapName'] if _map['GbxMapName'] != '?' else _map['Name'],
				author=_map['Username'],
				envir=_map['EnvironmentName'],
				awards='$fff🏆 {}'.format(_map['AwardCount']) if _map['AwardCount'] > 0 else "",
				difficulty=_map['DifficultyName'],
				maptype=_map['MapType'],
				style=_map['StyleName']
			) for _map in infos]

		if refresh:
			await self.refresh(self.player)


class MxPacksListView(ManualListView):
	def __init__(self, app, player, api):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.contrib.mx.app.RealMX
		"""
		super().__init__()
		self.manager = app.context.ui
		self.player = player
		self.app = app
		self.api = api

		self.template_name = 'mx/search.xml'
		self.response_future = asyncio.Future()

		self.cache = None
		self.has_data = False

		self.search_map = None
		self.search_author = None
		self.provide_search = True

		self.fields = [
			{
				'name': 'ID',
				'index': 'mxid',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label'
			},
			{
				'name': 'Pack Name',
				'index': 'name',
				'sorting': True,
				'searching': False,
				'width': 55,
				'type': 'label'
			},
			{
				'name': 'Author',
				'index': 'author',
				'sorting': True,
				'searching': False,
				'width': 40,
				'type': 'label',
			},
			{
				'name': 'Video',
				'index': 'videourl',
				'sorting': False,
				'searching': False,
				'width': 25,
				'type': 'label',
				'safe': True
			},
			{
				'name': 'Maps',
				'index': 'mapcount',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label'
			}
		]

		self.sort_field = None
		self.child = None
		self.subscribe("mx_search", self.action_search)

	async def get_title(self):
		return '🔍 Search {}'.format(self.app.site_name)

	async def get_data(self):
		if not self.has_data:
			# First opening, request the data.
			await self.do_search(refresh=False)
			self.has_data = True

		return self.cache

	async def get_object_data(self):
		data = await super().get_object_data()
		data['search_map'] = self.search_map
		data['search_author'] = self.search_author
		return data

	async def display(self, player=None):
		return await super().display(player or self.player)

	async def get_actions(self):
		return [
			{
				'name': 'Install pack',
				'type': 'label',
				'text': 'Install',
				'width': 12,
				'action': self.action_install,
				'safe': True
			}
		]

	async def action_install(self, user, values, map, *args, **kwargs):
		await self.app.instance.command_manager.execute(
			user,
			'//{}pack add'.format(self.app.namespace),
			str(map['mxid'])
		)

	async def action_search(self, user, action, values, *args, **kwargs):
		self.search_map = values['map']
		self.search_author = values['author']

		if values['map'] == "Search Map...":
			self.search_map = None
		if values['author'] == "Search Author...":
			self.search_author = None

		await self.do_search(self.search_map, self.search_author)

	async def do_search(self, name=None, username=None, refresh=True, **terms):
		try:
			options = {
				"api": "on",
				"mode": 0,
				"limit": 100,
			}

			if name is not None:
				options['name'] = name

			if username is not None:
				options['username'] = username

			infos = await self.api.search_pack(options)
			if len(infos) == 0:
				raise MXMapNotFound("No results for search")

		except MXMapNotFound as e:
			message = '$f00Error requesting {}-API: Map not found!'.format(self.app.site_short_name)
			await self.app.instance.chat(message, self.player)
			logger.debug('{}-API: Map not found: {}'.format(self.app.site_short_name, str(e)))
			return None
		except MXInvalidResponse as e:
			message = '$f00Error requesting {}-API: Got an invalid response!'.format(self.app.site_short_name)
			await self.app.instance.chat(message, self.player)
			logger.warning('{}-API: Invalid response: {}'.format(self.app.site_short_name, str(e)))
			return None

		self.cache = [dict(
				mxid=_map['ID'],
				name=_map['Name'],
				author=_map['Username'],
				mapcount=_map['TrackCount'],
				typename=_map['TypeName'],
				style=_map['StyleName'],
				videourl="$l[{video}]Video$l".format(video=_map['VideoURL']) if len(_map['VideoURL']) > 0 else "",
				unreleased='{}'.format(_map['Unreleased']),
				request='{}'.format(_map['Request'])
			) for _map in infos]

		if refresh:
			await self.refresh(self.player)


class MxStatusListView(ManualListView):
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	def __init__(self, app, api):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.contrib.mx.app.RealMX
		"""
		super().__init__()
		self.manager = app.context.ui
		self.cache = None
		self.app = app
		self.api = api

	async def get_title(self):
		return 'Server maps status on {}'.format(self.app.site_name)

	async def get_fields(self):
		fields = [
			{
				'name': 'ID',
				'index': 'index',
				'sorting': True,
				'searching': True,
				'width': 15,
				'type': 'label'
			},
			{
				'name': 'Map',
				'index': 'map_name',
				'sorting': True,
				'searching': True,
				'width': 91.5,
				'type': 'label'
			},
			{
				'name': 'On Server',
				'index': 'updated_on_server',
				'sorting': True,
				'searching': False,
				'width': 33,
				'type': 'label'
			},
			{
				'name': '{} Version'.format(self.app.site_short_name),
				'index': 'mx_version',
				'sorting': True,
				'searching': False,
				'width': 33,
				'type': 'label'
			},
			{
				'name': 'Status',
				'index': 'version_match',
				'sorting': True,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
		]

		# Can only update the map via MX if it's possible to remove the current version.
		if 'admin' in self.app.instance.apps.apps:
			fields.append({
				'name': 'Update',
				'index': 'action_update_content',
				'sorting': False,
				'searching': False,
				'width': 20,
				'type': 'label',
				'action': self.action_update_map
			})

		return fields

	async def action_update_map(self, player, values, instance, **kwargs):
		# Check if the map could be updated.
		if instance['action_update'] is True:
			# Ask for confirmation.
			cancel = bool(
				await ask_confirmation(player, 'Are you sure you want to update map \'{}\'$z$s to the version from {}?'.format(
					instance['map_name'],
					self.app.site_short_name
				), size='sm')
			)
			if cancel is True:
				return

			folders = None
			if 'jukebox' in self.app.instance.apps.apps:
				# Check if the map was part of a map folder.
				# Remove the current version and add the new version to the folders.
				folders = await self.app.instance.apps.apps['jukebox'].folder_manager.get_folders_containing_map(instance['map_id'])
				if folders is not None and len(folders) != 0:
					for folder in folders:
						await self.app.instance.apps.apps['jukebox'].folder_manager.remove_map_from_folder(folder.id, instance['map_id'])

			# Remove the current version from the server.
			mock_remove = namedtuple("data", ["nr"])
			await self.app.instance.apps.apps['admin'].map.remove_map(player, mock_remove(nr=instance['map_id']))

			# Add the new version from MX.
			mock_add = namedtuple("data", ["maps"])
			added_map = await self.app.add_mx_map(player, mock_add(maps=[instance['index']]))

			# If the map could be added and was part of folders, update the folders to contain the new version.
			if added_map is not None and len(added_map) == 1:
				if folders is not None and len(folders) != 0:
					for folder in folders:
						await self.app.instance.apps.apps['jukebox'].folder_manager.add_map_to_folder(folder.id, added_map[0].id)

			# Update the current view.
			await self.refresh(player=player)

	async def get_data(self):
		if self.cache:
			print('cached')
			return self.cache

		# Determine which maps on the server could be found on MX (filter those with an ID attached).
		mx_maps_on_server = [map for map in self.app.instance.map_manager.maps if map.mx_id is not None]
		try:
			mx_maps_info = await self.api.map_info(*[map.mx_id for map in mx_maps_on_server])
		except Exception as e:
			mx_maps_info = list()
			logger.error('Could not retrieve map info from MX/TM API: {}'.format(str(e)))

		# Loop through the MX-compatible maps on the server.
		items = []
		for item in mx_maps_on_server:
			# Initialize view data fields.
			version_match = ''
			version_match_order = None
			mx_version_date = ''
			action_update = False

			# Get MX information for the map (gets None if it couldn't be found).
			mx_map = next((mx_map_info for mx_map_info in mx_maps_info if mx_map_info[0] == item.mx_id), None)

			if mx_map is None:
				version_match = 'Not on {}'.format(self.app.site_short_name)
				version_match_order = 1
			else:
				date_format = '%Y-%m-%dT%H:%M:%S'
				if '.' in mx_map[1]['UpdatedAt']:
					date_format = '%Y-%m-%dT%H:%M:%S.%f'
				mx_version_date = datetime.strptime(mx_map[1]['UpdatedAt'], date_format).strftime("%Y-%m-%d %H:%M:%S")
				mx_map_uid = mx_map[1]['TrackUID'] if 'TrackUID' in mx_map[1] else mx_map[1]['MapUID']

				if mx_map_uid == item.uid:
					version_match = '$0a0Up-to-date'
					version_match_order = 2
				else:
					version_match = '$00fNew version'
					version_match_order = 0
					action_update = True

			action_update_content = '🔁 Update' if action_update else '          -'
			items.append({'map_id': item.id, 'index': item.mx_id, 'map_name': item.name, 'version_match': version_match, 'version_match_order': version_match_order,
				'updated_on_server': item.updated_at, 'mx_version': mx_version_date, 'action_update': action_update, 'action_update_content': action_update_content})

		# Initially sort the maps based on the 'version_match_order': New version -> Not on MX -> Up-to-date.
		items.sort(key=lambda x: x['version_match_order'])
		self.cache = items
		return self.cache

	async def destroy(self):
		self.cache = None
		return await super().destroy()

	def destroy_sync(self):
		self.cache = None
		return super().destroy_sync()


class MxAwardWidget(WidgetView):
	"""
	Award widget.
	"""

	widget_x = 63
	widget_y = -67.5
	z_index = 100
	template_name = 'mx/award.xml'
	mx_id = None

	def __init__(self, app):
		"""
		Initializes the widget.

		:param app: the MX application (plugin)
		"""

		super().__init__(app.context.ui)
		self.app = app
		self.id = 'pyplanet__widgets_mxaward'

	async def get_context_data(self):
		"""
		Called to request data to display in the widget.
		"""

		context = await super().get_context_data()

		context.update({
			'map_name': self.app.instance.map_manager.current_map.name,
			'site_name': self.app.site_short_name,
			'award_url': "{}/maps/{}/#award".format(self.app.api.base_url(), self.mx_id)
		})

		return context
