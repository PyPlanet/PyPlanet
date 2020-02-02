"""
MX List Views.
"""
import asyncio
import logging
import re

from pyplanet.views.generics import ManualListView, ask_confirmation
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
from datetime import datetime
from collections import namedtuple

logger = logging.getLogger(__name__)


class MxSearchListView(ManualListView):
	title = '🔍 Search Mania-Exchange'

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
		self.style = "-1"
		self.mode = "0"

		self.provide_search = True

		self.fields = [
			{
				'name': "#",
				'type': "checkbox",
				'width': 6,
				'sorting': False,
				'index': 'disabled'
			},
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

		if self.app.instance.game.game == "tm":
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

	async def get_buttons(self):
		buttons = [
			{
				'title': ' Selected',
				'width': 20,
				'action': self.action_install_selected,
				'require_confirm': True
			}
		]
		return buttons

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
		data['mode'] = [
			{
				"text": "Default",
				"value": "0"
			},
			{
				"text": "Latest Tracks",
				"value": "2"
			},
			{
				"text": "Recently Awarded",
				"value": "3"
			},
			{
				"text": "Best Maps of the Month",
				"value": "5"
			},
			{
				"text": "Best Karma of Month",
				"value": "22"
			}
		]
		if self.app.instance.game.game == "tm":
			data['styles'] = [
				{
					"text": "Select...",
					"value": "-1"
				},
				{
					"text": "Race",
					"value": "1"
				},
				{
					"text": "Fullspeed",
					"value": "2"
				},
				{
					"text": "Tech",
					"value": "3"
				},
				{
					"text": "RPG",
					"value": "4"
				},
				{
					"text": "LOL",
					"value": "5"
				},
				{
					"text": "Press Forward",
					"value": "6"
				},
				{
					"text": "Speedtech",
					"value": "7"
				},
				{
					"text": "Multilap",
					"value": "8"
				},
				{
					"text": "Offroad",
					"value": "9"
				},
				{
					"text": "Trial",
					"value": "10"
				},
			]
		else:
			data['styles'] = [
				{
					"text": "Select...",
					"value": "-1"
				},
				{
					"text": "Solo",
					"value": "1"
				},
				{
					"text": "Team",
					"value": "2"
				},
				{
					"text": "Versus",
					"value": "3"
				},
				{
					"text": "Other",
					"value": "4"
				},
			]

		data['style_index'] = 0
		i = 0
		for i, val in enumerate(data['styles']):  # for name, age in dictionary.iteritems():  (for Python 2.x)
			if self.style == val['value']:
				data['style_index'] = i
			i += 1

		data['mode_index'] = 0
		for i, val in enumerate(data['mode']):  # for name, age in dictionary.iteritems():  (for Python 2.x)
			if self.mode == val['value']:
				data['mode_index'] = i
			i += 1

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
				'require_confirm': True,
				'safe': True
			}
		]

	async def action_install_selected(self, player, values, **kwargs):
		for key, value in values.items():
			if key.startswith('checkbox_') and value == '1':
				match = re.search('^checkbox_([0-9]+)_([0-9]+)$', key)
				if len(match.groups()) != 2:
					return

				row = int(match.group(1))
				await self.app.instance.command_manager.execute(player, '//mx add {}'.format(self.objects[row]['mxid']))

	async def action_install(self, user, values, map, *args, **kwargs):
		await self.app.instance.command_manager.execute(user, '//mx add', str(map['mxid']))

	async def action_search(self, user, action, values, *args, **kwargs):
		self.search_map = values['map']
		self.search_author = values['author']
		self.mode = values['mode']
		self.style = values['style']

		if values['map'] == "Search Map...":
			self.search_map = None
		if values['author'] == "Search Author...":
			self.search_author = None

		await self.do_search(self.search_map, self.search_author)

	async def do_search(self, trackname=None, authorname=None, refresh=True, **terms):
		try:
			options = {
				"api": "on",
				"mode": self.mode,
				"gv": 1,
				"limit": 100,
				"tpack": self.app.instance.game.dedicated_title.split("@", 1)[0]
			}
			if self.style is not "-1":
				options['style'] = self.style

			if trackname is not None:
				options['trackname'] = trackname

			if authorname is not None:
				options['anyauthor'] = authorname

			infos = await self.api.search(options)
			if len(infos) == 0:
				raise MXMapNotFound("No results for search")

		except MXMapNotFound as e:
			message = '$f00Error requesting MX-API: Map not found!'
			await self.app.instance.chat(message, self.player)
			logger.debug('MX-API: Map not found: {}'.format(str(e)))
			return None
		except MXInvalidResponse as e:
			message = '$f00Error requesting MX-API: Got an invalid response!'
			await self.app.instance.chat(message, self.player)
			logger.warning('MX-API: Invalid response: {}'.format(str(e)))
			return None
		if self.app.instance.game.game == "tm":
			self.cache = [dict(
				mxid=_map['TrackID'],
				name=_map['Name'],
				gbxname=_map['GbxMapName'],
				author=_map['Username'],
				envir=_map['EnvironmentName'],
				awards='$fff🏆 {}'.format(_map['AwardCount']) if _map['AwardCount'] > 0 else "",
				length=_map['LengthName'],
				difficulty=_map['DifficultyName'],
				maptype=_map['MapType'],
				style=_map['StyleName'],
				disabled=0
			) for _map in infos]
		else:
			self.cache = [dict(
				mxid=_map['TrackID'],
				name=_map['Name'],
				gbxname=_map['GbxMapName'],
				author=_map['Username'],
				envir=_map['EnvironmentName'],
				awards='$fff🏆 {}'.format(_map['AwardCount']) if _map['AwardCount'] > 0 else "",
				difficulty=_map['DifficultyName'],
				maptype=_map['MapType'],
				style=_map['StyleName'],
				disabled=0
			) for _map in infos]

		if refresh:
			await self.refresh(self.player)


class MxPacksListView(ManualListView):
	title = '🔍 Search Mania-Exchange'

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

		self.template_name = 'mx/search_pack.xml'
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
				'type': 'label',
			}
		]

		self.sort_field = None
		self.child = None
		self.subscribe("mx_search", self.action_search)

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
		await self.app.instance.command_manager.execute(user, '//mxpack add', str(map['mxid']))

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
			message = '$f00Error requesting MX-API: Map not found!'
			await self.app.instance.chat(message, self.player)
			logger.debug('MX-API: Map not found: {}'.format(str(e)))
			return None
		except MXInvalidResponse as e:
			message = '$f00Error requesting MX-API: Got an invalid response!'
			await self.app.instance.chat(message, self.player)
			logger.warning('MX-API: Invalid response: {}'.format(str(e)))
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
	title = 'Server maps status on Mania-Exchange'
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
		self.app = app
		self.api = api

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
				'name': 'MX Version',
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
			cancel = bool(await ask_confirmation(player,
												 'Are you sure you want to update map \'{}\'$z$s to the version from MX?'.format(
													 instance['map_name']
												 ), size='sm'))
			if cancel is True:
				return

			# Remove the current version from the server.
			mock_remove = namedtuple("data", ["nr"])
			await self.app.instance.apps.apps['admin'].map.remove_map(player, mock_remove(nr=instance['map_id']))

			# Add the new version from MX.
			mock_add = namedtuple("data", ["maps"])
			await self.app.add_mx_map(player, mock_add(maps=[instance['index']]))

			# Update the current view.
			await self.refresh(player=player)

	async def get_data(self):
		# Determine which maps on the server could be found on MX (filter those with an ID attached).
		mx_maps_on_server = [map for map in self.app.instance.map_manager.maps if map.mx_id is not None]
		mx_maps_info = await self.api.map_info([map.mx_id for map in mx_maps_on_server])

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
				version_match = 'Not on MX'
				version_match_order = 1
			else:
				mx_version_date = datetime.strptime(mx_map[1]['UpdatedAt'], '%Y-%m-%dT%H:%M:%S.%f').strftime(
					"%Y-%m-%d %H:%M:%S")

				if mx_map[1]['TrackUID'] == item.uid:
					version_match = '$0a0Up-to-date'
					version_match_order = 2
				else:
					version_match = '$00fNew version'
					version_match_order = 0
					action_update = True

			action_update_content = '🔁 Update' if action_update else '          -'
			items.append({'map_id': item.id, 'index': item.mx_id, 'map_name': item.name, 'version_match': version_match,
						  'version_match_order': version_match_order,
						  'updated_on_server': item.updated_at, 'mx_version': mx_version_date,
						  'action_update': action_update, 'action_update_content': action_update_content})

		# Initially sort the maps based on the 'version_match_order': New version -> Not on MX -> Up-to-date.
		items.sort(key=lambda x: x['version_match_order'])
		return items
