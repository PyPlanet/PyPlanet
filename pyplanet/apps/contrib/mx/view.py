"""
Mode Settings Views.
"""
import asyncio
import logging

from pyplanet.views.generics import ManualListView
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
import html

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
				name=self.trim(_map['Name']),
				gbxname=_map['GbxMapName'],
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
				name=self.trim(_map['Name']),
				gbxname=_map['GbxMapName'],
				author=_map['Username'],
				envir=_map['EnvironmentName'],
				awards='$fff🏆 {}'.format(_map['AwardCount']) if _map['AwardCount'] > 0 else "",
				difficulty=_map['DifficultyName'],
				maptype=_map['MapType'],
				style=_map['StyleName']
			) for _map in infos]

		if refresh:
			await self.refresh(self.player)

	def trim(self, string):
		return html.escape(string)


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
				'name': 'Environment',
				'index': 'environment',
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
				'name': 'Install pack',
				'type': 'label',
				'text': 'Install',
				'width': 12,
				'action': self.action_install,
				'safe': True,
				'require_confirm': True
			}
		]

	async def action_install(self, user, values, map, *args, **kwargs):
		await self.app.instance.command_manager.execute(user, '//mxpack add', str(map['mxid']))

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
			environment=_map['Titlepack'] if _map['Titlepack'] else _map['EnvironmentName'],
			# videourl="$l[{video}]Video$l".format(video=_map['VideoURL']) if len(_map['VideoURL']) > 0 else "",
			videourl="",
			unreleased='{}'.format(_map['Unreleased']),
			request='{}'.format(_map['Request'])
		) for _map in infos]

		if refresh:
			await self.refresh(self.player)

	def trim(self, string):
		return html.escape(string)
