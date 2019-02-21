"""
Mode Settings Views.
"""
import asyncio
from pyplanet.views.generics import ManualListView
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse


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
		self.provide_search = False
		self.fields = [
			{
				'name': 'Map',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 60,
				'type': 'label'
			},
			{
				'name': 'Author',
				'index': 'author',
				'sorting': True,
				'searching': True,
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
				'name': 'Length',
				'index': 'length',
				'sorting': True,
				'searching': False,
				'width': 25,
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
		self.sort_field = None
		self.child = None
		self.subscribe("mx_search", self.action_search)

	async def get_data(self):
		if self.cache:
			return self.cache

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
		await self.app.instance.command_manager.execute(user, '//mx add', str(map['mxid']))

	async def action_search(self, user, action, values, *args, **kwargs):
		mx_map = values['map']
		mx_author = values['author']

		if values['map'] == "Search Map...":
			mx_map = None
		if values['author'] == "Search Author...":
			mx_author = None

		# todo find a way to add mx_map and mx_author to context_data

		await self.do_search(mx_map, mx_author)

	async def do_search(self, trackname=None, authorname=None, **terms):
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

			print(options)
			infos = await self.api.search(options)
			if len(infos) == 0:
				raise MXMapNotFound("No results for search")

		except MXMapNotFound as e:
			print(str(e))
			return None
		except MXInvalidResponse as e:
			print(str(e))
			return None

		self.cache = [dict(
			mxid=_map['TrackID'],
			name=_map['Name'],
			author=_map['Username'],
			envir=_map['EnvironmentName'],
			awards='$fff🏆 {}'.format(_map['AwardCount']) if _map['AwardCount'] > 0 else "",
			length=_map['LengthName'],
			difficulty=_map['DifficultyName'],
			maptype=_map['MapType'],
			style=_map['StyleName']
		) for _map in infos]

		await self.refresh(self.player)
