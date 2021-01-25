import math

from pyplanet.views.generics.list import ManualListView
from pyplanet.views.generics.widget import TimesWidgetView


class RankListView(ManualListView):
	title = 'Ranks on the server'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'
	rank_list = []
	player = None

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': False,
				'searching': True,
				'width': 10,
				'type': 'label'
			},
			{
				'name': 'nickname',
				'index': 'nickname',
				'sorting': False,
				'searching': True,
				'width': 70,
				'type': 'label'
			},
			{
				'name': 'login',
				'index': 'login',
				'sorting': False,
				'searching': True,
				'width': 50,
				'type': 'label'
			},
			{
				'name': 'average',
				'index': 'avg',
				'sorting': False,
				'searching': True,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'difference',
				'index': 'diff',
				'sorting': False,
				'searching': True,
				'width': 50,
				'type': 'label'
			}
		]

	def __init__(self, app, player_index, data):
		super().__init__()
		self.app = app
		self.manager = app.context.ui
		self.player_index = player_index
		self.results = data

		self.provide_search = True
		self.provide_find_self = True
		self.subscribe('find_own', self._find_own)

	async def get_data(self):
		return self.results

	async def _find_own(self, player, *args, **kwargs):
		self.page = self.player_index // self.num_per_page + 1
		await self.refresh(player)


class RankWidget(TimesWidgetView):
	widget_x = -160
	widget_y = 12.5
	z_index = 30
	size_x = 38
	size_y = 55.5
	top_entries = 5
	title = 'Server Rank'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_serverrank'

		self.action = app.ranks
		self.rank_amount = 15

	async def get_player_data(self):
		data = await super().get_player_data()

		if self.app.instance.performance_mode:
			return data

		server_rank_data = await self.app.get_rank_data()
		# Columns: - index - sum - avg - nickname - login
		server_ranks = dict()

		for player in self.app.instance.player_manager.online:
			player_rank = [x for x in server_rank_data if x.login == player.login]
			player_index = (len(server_rank_data) + 1)
			list_ranks = list()
			if len(player_rank) > 0:
				# Set player index if there is a rank
				player_index = (server_rank_data.index(player_rank[0]) + 1)

			ranks = list(server_rank_data[:self.top_entries])
			custom_start_index = None
			if player_index > len(server_rank_data):
				# No personal rank, get the last records
				records_start = (len(server_rank_data) - self.rank_amount + self.top_entries)
				# If start of current slice is in the top entries, add more ranks below
				if records_start < self.top_entries:
					records_start = self.top_entries

				ranks += list(server_rank_data[records_start:])
				custom_start_index = (records_start + 1)
			else:
				if player_index <= self.top_entries:
					# Player record is in top X, get following ranks (top entries + 1 onwards)
					ranks += server_rank_data[self.top_entries:self.rank_amount]
					custom_start_index = (self.top_entries + 1)
				else:
					# Player rank is not in top X, get ranks around player rank
					# Same amount above the rank as below, except when not possible (favors above)
					ranks_to_fill = (self.rank_amount - self.top_entries)
					start_point = ((player_index - math.ceil((ranks_to_fill - 1) / 2)) - 1)
					end_point = ((player_index + math.floor((ranks_to_fill - 1) / 2)) - 1)

					# If end of current slice is outside the list, add more records above
					if end_point > len(server_rank_data):
						end_difference = (end_point - len(server_rank_data))
						start_point = (start_point - end_difference)
					# If start of current slice is in the top entries, add more records below
					if start_point < self.top_entries:
						start_point = self.top_entries

					ranks += server_rank_data[start_point:(start_point + ranks_to_fill)]
					custom_start_index = (start_point + 1)

			index = 1
			for rank in ranks:
				list_rank = dict()
				list_rank['index'] = index
				list_rank['color'] = '$fff'
				if index <= self.top_entries:
					list_rank['color'] = '$ff0'
				if index == player_index:
					list_rank['color'] = '$0f3'
				list_rank['nickname'] = rank['nickname']
				list_rank['score'] = (rank['avg'])
				if index == self.top_entries:
					index = custom_start_index
				else:
					index += 1
				list_ranks.append(list_rank)

			server_ranks[player.login] = {'times': list_ranks}

		data.update(server_ranks)

		return data

	async def get_context_data(self):
		context = await super().get_context_data()

		server_rank_data = await self.app.get_rank_data()

		# Add facts.
		context.update({
			'top_entries': self.top_entries
		})

		if self.app.instance.performance_mode:
			list_ranks = list()
			ranks = list(server_rank_data[:self.rank_amount])

			index = 1
			for rank in ranks:
				list_rank = dict()
				list_rank['index'] = index
				list_rank['color'] = '$fff'
				if index <= self.top_entries:
					list_rank['color'] = '$ff0'
				list_rank['nickname'] = rank['nickname']
				list_rank['score'] = rank['avg']
				index += 1
				list_ranks.append(list_rank)

			context.update({
				'times': list_ranks
			})

		return context

	async def action_recordlist(self, player, **kwargs):
		await self.app.show_records_list(player)
