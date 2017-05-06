from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.utils.style import percentage_color, rgb_to_hex
from pyplanet.views.generics.widget import WidgetView
from pyplanet.views.generics.list import ManualListView


class KarmaWidget(WidgetView):
	widget_x = 124
	widget_y = 75
	size_x = 38
	size_y = 18
	title = None  # 'Map karma'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	template_name = 'karma/karma.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_karma'

		self.action = self.action_whokarma
		self.subscribe('vote_positive', self.action_vote_positive)
		self.subscribe('vote_negative', self.action_vote_negative)

	async def get_context_data(self):
		context = await super().get_context_data()

		karma_percentage = round((len(self.app.current_positive_votes) / (len(self.app.current_votes))) * 100, 2) \
			if len(self.app.current_votes) > 0 else 0

		color = percentage_color(karma_percentage)
		bar_color = rgb_to_hex(color)
		karma_text_color = '$fff'
		if self.app.current_karma > 0:
			karma_text_color = '$3f3'
		elif self.app.current_karma < 0:
			karma_text_color = '$f00'

		context.update({
			'current_karma': self.app.current_karma,
			'karma_percentage': karma_percentage,
			'progress_color': bar_color,
			'progress_percentage': karma_percentage if karma_percentage != 0 else 5,
			'karma_text_color': karma_text_color,
			'positive_votes': len(self.app.current_positive_votes),
			'negative_votes': len(self.app.current_negative_votes)
		})

		return context

	async def get_player_data(self):
		data = await super().get_player_data()
		votes = dict()

		for player in self.app.instance.player_manager.online:
			player_vote = [x for x in self.app.current_votes if x.player_id == player.get_id()]
			if len(player_vote) > 0:
				votes[player.login] = {'player_vote': player_vote[0].score}
			else:
				votes[player.login] = {'player_vote': 0}

		data.update(votes)

		return data

	async def action_whokarma(self, player, **kwargs):
		await self.app.show_map_list(player)

	async def action_vote_positive(self, player, action, values, **kwargs):
		await self.app.player_chat(player, '++', False)

	async def action_vote_negative(self, player, action, values, **kwargs):
		await self.app.player_chat(player, '--', False)


class KarmaListView(ManualListView):
	title = 'Karma votes on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	fields = [
		{
			'name': 'Player',
			'index': 'nickname',
			'sorting': False,
			'searching': True,
			'width': 70
		},
		{
			'name': 'Vote',
			'index': 'vote',
			'sorting': True,
			'searching': False,
			'width': 30,
			'type': 'label'
		}
	]

	def __init__(self, app, map):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.map = map

	async def get_title(self):
		return 'Karma votes on {}'.format(self.map.name)

	async def get_data(self):
		karma = await Karma.execute(
			Karma
				.select(Karma, Player)
				.join(Player)
				.where(Karma.map == self.map)
		)
		return [
			{'nickname': item.player.nickname, 'vote': '++' if item.score else '--'} for item in karma
		]
