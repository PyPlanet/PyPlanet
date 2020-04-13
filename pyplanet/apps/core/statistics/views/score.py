from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.apps.core.statistics.models import Score
from pyplanet.utils import times
from pyplanet.views.generics.list import ManualListView


class StatsScoresListView(ManualListView):
	title = 'Personal time progression on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player):
		"""
		Init score list view.

		:param player: Player instance.
		:param app: App instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		super().__init__(self)

		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False

	async def get_data(self):
		score_list = await Score.objects.execute(
			Score.select(Score, Player)
				.join(Player)
				.where(Score.map == self.app.instance.map_manager.current_map.get_id())
				.order_by(Score.created_at.asc())
		)

		scores_list = list(score_list)

		personal_list = [s for s in scores_list if s.player.id == self.player.get_id()]

		if len(personal_list) == 0:
			message = '$i$f00There are no personal scores available for $fff{}$z$s$f00$i!'.format(self.app.instance.map_manager.current_map.name)
			await self.app.instance.chat(message, self.player)
			return

		local_record = min([s.score for s in scores_list])

		scores = list()
		last_best = 0
		last_best_index = 1
		personal_best = min([s.score for s in personal_list])
		for score_in_list in personal_list:
			historical_local = min([s.score for s in scores_list if s.created_at <= score_in_list.created_at])

			score = dict()
			score['index'] = ''
			score['score'] = times.format_time(score_in_list.score)
			score['created_at'] = score_in_list.created_at.strftime('%d-%m-%Y %H:%M:%S')
			score['difference_to_pb'] = times.format_time((score_in_list.score - personal_best))
			score['difference_to_prev'] = ''
			score['difference_to_local'] = times.format_time((score_in_list.score - local_record))
			score['historical_local'] = times.format_time(historical_local)
			score['difference_to_hist_local'] = times.format_time((score_in_list.score - historical_local))

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

			if score_in_list.score == local_record:
				score['difference_to_local'] = ''
			else:
				score['difference_to_local'] = '$f00+ {}'.format(score['difference_to_local'])

			if score_in_list.score == historical_local:
				score['difference_to_hist_local'] = ''
			else:
				score['difference_to_hist_local'] = '$f00+ {}'.format(score['difference_to_hist_local'])

			if score_in_list.score == personal_best:
				score['index'] = 'PB'
				score['difference_to_pb'] = ''
			else:
				score['difference_to_pb'] = '$f00+ {}'.format(score['difference_to_pb'])

			scores.append(score)

		return scores

	async def get_fields(self):
		return [
			{
				'name': '#',
				'index': 'index',
				'sorting': False,
				'searching': False,
				'width': 6,
				'type': 'label'
			},
			{
				'name': 'Time',
				'index': 'score',
				'sorting': False,
				'searching': False,
				'width': 25,
				'type': 'label'
			},
			{
				'name': 'From PB',
				'index': 'difference_to_pb',
				'sorting': False,
				'searching': False,
				'width': 28,
				'type': 'label'
			},
			{
				'name': 'From prev. PB',
				'index': 'difference_to_prev',
				'sorting': False,
				'searching': False,
				'width': 34,
				'type': 'label'
			},
			{
				'name': 'From Local',
				'index': 'difference_to_local',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'Hist. Local',
				'index': 'historical_local',
				'sorting': False,
				'searching': False,
				'width': 28,
				'type': 'label'
			},
			{
				'name': 'From hist. Local',
				'index': 'difference_to_hist_local',
				'sorting': False,
				'searching': False,
				'width': 34,
				'type': 'label'
			},
			{
				'name': 'Driven at',
				'index': 'created_at',
				'sorting': False,
				'searching': False,
				'width': 40,
				'type': 'label'
			},
		]


class CheckpointComparisonView(ManualListView):
	title = 'Checkpoint comparison on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, player):
		"""
		Init score list view.

		:param player: Player instance.
		:param app: App instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		super().__init__(self)

		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False

	async def get_data(self):
		score_list = await Score.objects.execute(
			Score.select(Score, Player)
				.join(Player)
				.where(Score.map == self.app.instance.map_manager.current_map.get_id())
				.order_by(Score.score.asc())
		)

		scores_list = list(score_list)
		for score in scores_list:
			score_checkpoints = score.checkpoints.split(',')
			score.checkpoints = [int(y) - int(x) for x, y in zip(score_checkpoints, score_checkpoints[1:])]  # TODO: Improve performance of this code block.
			score.checkpoints.insert(0, int(score_checkpoints[0]))

		personal_list = [s for s in scores_list if s.player.id == self.player.get_id()]

		local_record = next(iter(scores_list or []), None)
		personal_best = next(iter(personal_list or []), None)

		checkpoints = list()
		total_pb = 0
		total_local = 0
		total_ideal = 0

		for checkpoint_index in range(0, self.app.instance.map_manager.current_map.num_checkpoints):
			pb_checkpoint = personal_best.checkpoints[checkpoint_index] if personal_best is not None else None
			local_checkpoint = local_record.checkpoints[checkpoint_index] if local_record is not None else None
			ideal_checkpoint = min([cp.checkpoints[checkpoint_index] for cp in scores_list]) if scores_list is not None and len(scores_list) > 0 else None
			ideal_record = [score for score in scores_list if score.checkpoints[checkpoint_index] == ideal_checkpoint][0] if scores_list is not None and len(scores_list) > 0 else None

			if pb_checkpoint is not None:
				total_pb += pb_checkpoint

			if local_checkpoint is not None:
				total_local += local_checkpoint
				total_ideal += ideal_checkpoint

			checkpoint = dict()
			checkpoint['index'] = (checkpoint_index + 1) if checkpoint_index < (self.app.instance.map_manager.current_map.num_checkpoints - 1) else 'Finish'
			checkpoint['personal_best'] = '{} ({})'.format(times.format_time(total_pb), times.format_time(pb_checkpoint)) if pb_checkpoint is not None else '-'
			checkpoint['local_record'] = '{} ({})'.format(times.format_time(total_local), times.format_time(local_checkpoint)) if local_checkpoint is not None else '-'
			checkpoint['local_record_driver'] = local_record.player.nickname if local_checkpoint is not None else '-'
			checkpoint['difference_to_local'] = '-'
			checkpoint['ideal'] = '{} ({})'.format(times.format_time(total_ideal), times.format_time(ideal_checkpoint)) if local_checkpoint is not None else '-'
			checkpoint['ideal_driver'] = ideal_record.player.nickname if local_checkpoint is not None else '-'
			checkpoint['difference_to_ideal'] = '-'

			if pb_checkpoint is not None:
				if total_pb > total_local:
					checkpoint['difference_to_local'] = '$f00+ {}'.format(times.format_time((total_pb - total_local)))
				else:
					checkpoint['difference_to_local'] = '$00f- {}'.format(times.format_time((total_local - total_pb)))

				if total_pb > total_ideal:
					checkpoint['difference_to_ideal'] = '$f00+ {}'.format(times.format_time((total_pb - total_ideal)))
				else:
					checkpoint['difference_to_ideal'] = '$00f- {}'.format(times.format_time((total_ideal - total_pb)))

			checkpoints.append(checkpoint)

		return checkpoints

	async def get_fields(self):
		return [
			{
				'name': 'CP #',
				'index': 'index',
				'sorting': False,
				'searching': False,
				'width': 15,
				'type': 'label'
			},
			{
				'name': 'Your PB',
				'index': 'personal_best',
				'sorting': False,
				'searching': False,
				'width': 32,
				'type': 'label'
			},
			{
				'name': 'Local Record',
				'index': 'local_record',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'Driver',
				'index': 'local_record_driver',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'From Local',
				'index': 'difference_to_local',
				'sorting': False,
				'searching': False,
				'width': 26,
				'type': 'label'
			},
			{
				'name': 'Ideal',
				'index': 'ideal',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'Driver',
				'index': 'ideal_driver',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'From Ideal',
				'index': 'difference_to_ideal',
				'sorting': False,
				'searching': False,
				'width': 26,
				'type': 'label'
			}
		]
