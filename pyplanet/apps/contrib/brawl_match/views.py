import asyncio

from pyplanet.apps.core.maniaplanet.models import Map, Player
from pyplanet.views.generics.list import ManualListView


class BrawlMapListView(ManualListView):
	model = Map
	title = 'Maps available to ban'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'
	# List of map uid's that the competition uses.
	map_list = []

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
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'width': 90,
				'type': 'label',
				'action': self.action_ban
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'search_strip_styles': True,
				'renderer': lambda row, field:
				row['author_login'],
				'width': 45,
			}
		]

	def __init__(self, app, maps):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.map_list = maps

	async def get_data(self):
		items = []
		for map_index, map_uid in enumerate(self.map_list, start=1):
			map = await self.app.instance.map_manager.get_map(map_uid)
			map_name = map.name
			map_author = map.author_login

			items.append({
				'index': map_index,
				'name': map_name,
				'author_login': map_author
			})
		return items



	async def action_ban(self, player, values, map_info, **kwargs):
		await self.app.register_match_task(self.app.remove_map_from_match, map_info)
		await self.app.instance.chat(f'{self.app.chat_prefix}Player '
								f'{player.nickname}$z$fff has just banned '
								f'{map_info["name"]}')
		# Maybe not an ideal solution, but works for now
		await self.hide([player.login])
		await self.app.register_match_task(self.app.next_ban)
		await self.destroy()

class BrawlPlayerListView(ManualListView):
	model = Player
	title = 'Players in the match'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'
	# List of players available to add to brawl match
	player_list = []

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
				'name': 'Nickname',
				'index': 'nickname',
				'sorting': True,
				'searching': True,
				'width': 100,
				'type': 'label',
				'action': self.action_add
			},
			{
				'name': 'Login',
				'index': 'login',
				'sorting': True,
				'searching': True,
				'width': 50,
				'type': 'label',
				'action': self.action_add
			}
		]

	async def get_data(self):
		return [
			{
				'index': index,
				'nickname': player.nickname,
				'login': player.login
			}
				for index, player in enumerate(
					self.app.instance.player_manager.online, start=1
				)

			]

	async def action_add(self, player, values, player_info, **kwargs):
		if len(self.app.match_players) < 3:
			await self.app.register_match_task(self.app.add_player_to_match, player, player_info)
		else:
			await self.app.register_match_task(self.app.add_player_to_match, player, player_info)
			# Maybe not an ideal solution, but works for now
			await self.hide([player.login])
			await self.app.register_match_task(self.app.start_ban_phase)
			await self.destroy()
