from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.apps.core.statistics.models import Score

from pyplanet.apps.contrib.statistics_scores.views import ScoresListView

from pyplanet.utils import times


class StatisticsScores(AppConfig):  # pragma: no cover
	name = 'pyplanet.apps.contrib.statistics_scores'
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='scoreprogression', aliases=['progression'], target=self.command_progression),
		)

	async def command_progression(self, player, data, **kwargs):
		score_list = await Score.objects.execute(
			Score.select(Score)
				.where(Score.map == self.instance.map_manager.current_map.get_id())
				.where(Score.player == player.get_id())
				.order_by(Score.created_at.asc())
		)

		if len(score_list) == 0:
			message = '$i$f00You have never finished $fff{}$z$s$f00$i!'.format(self.instance.map_manager.current_map.name)
			await self.instance.chat(message, player)
			return

		scores = []
		last_best = 0
		last_best_index = 1
		personal_best = min([s.score for s in score_list])
		for score_in_list in score_list:
			score = dict()
			score['index'] = ''
			score['score'] = times.format_time(score_in_list.score)
			score['created_at'] = score_in_list.created_at.strftime('%d-%m-%Y %H:%M:%S')
			score['difference_to_pb'] = times.format_time((score_in_list.score - personal_best))
			score['difference_to_prev'] = ''

			if last_best == 0:
				score['index'] = last_best_index
				last_best = score_in_list.score
				last_best_index += 1
			elif score_in_list.score < last_best:
				score['index'] = last_best_index
				score['difference_to_prev'] = '$00f- {}'.format(times.format_time((last_best - score_in_list.score)))
				last_best = score_in_list.score
				last_best_index += 1
			else:
				score['difference_to_prev'] = '$f00+ {}'.format(times.format_time((score_in_list.score - last_best)))

			if score_in_list.score == personal_best:
				score['index'] = 'PB'
				score['difference_to_pb'] = ''
			else:
				score['difference_to_pb'] = '$f00+ {}'.format(score['difference_to_pb'])

			scores.append(score)

		view = ScoresListView(self, list(reversed(scores)))
		await view.display(player=player.login)
