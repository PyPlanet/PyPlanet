"""
Mode Settings Views.
"""

from pyplanet.views.generics import ManualListView


class MxSearchListView(ManualListView):
	title = 'Search Mania-Exchange'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	def __init__(self, app, player, maps):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.contrib.mx.app.RealMX
		:type api: pyplanet.apps.contrib.mx.api.MXApi
		"""
		super().__init__()
		self.manager = app.context.ui
		self.player = player
		self.app = app
		self.maps = maps
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
				'width': 15,
				'type': 'label',
				'safe': True
			},
			{
				'name': 'Awards',
				'index': 'awards',
				'sorting': True,
				'searching': False,
				'width': 35,
				'type': 'label'
			},
			{
				'name': 'Length',
				'index': 'length',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label'
			},
		]
		self.sort_field = self.fields[2]
		self.child = None

	async def get_data(self):
		return [dict(
			mxid=_map['TrackID'],
			name=_map['Name'],
			author=_map['Username'],
			envir=_map['EnvironmentName'],
			awards='$ff0ðŸ† $fff{}'.format(_map['AwardCount']) if _map['AwardCount'] < 0 else "",
			length=_map['LengthName'],
			difficulty=_map['DifficultyName'],
			maptype=_map['MapType'],
			style=_map['StyleName']
		) for _map in self.maps]

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
		print(map)
		await self.app.instance.command_manager.execute(user, '//mx add', str(map['mxid']))
