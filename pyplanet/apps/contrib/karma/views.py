from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.generics.widget import WidgetView
from pyplanet.views.generics.list import ManualListView


class KarmaWidget(WidgetView):
	widget_x = 124
	widget_y = 70
	size_x = 38
	size_y = 20.5
	title = 'Map karma'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Buddies'

	template_name = 'karma/karma.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_karma'

		self.action = self.action_whokarma

	async def get_context_data(self):
		map = self.app.instance.map_manager.current_map

		karma_color = '$fff'
		if self.app.current_karma > 0:
			karma_color = '$3f3'
		elif self.app.current_karma < 0:
			karma_color = '$f00'

		context = await super().get_context_data()
		context.update({
			'current_karma': self.app.current_karma,
			'current_karma_percentage': round((len(self.app.current_positive_votes) / (len(self.app.current_votes))) * 100, 1),
			'karma_color': karma_color,
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
		self.manager = app.ui
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
