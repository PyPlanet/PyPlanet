from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.live_rankings.views import LiveRankingsWidget

from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from pyplanet.contrib.setting import Setting


class LiveRankings(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_rankings = []
		self.points_repartition = []
		self.current_finishes = []
		self.widget = None
		self.dedimania_enabled = False

		self.setting_rankings_amount = Setting(
			'rankings_amount', 'Amount of rankings to display', Setting.CAT_BEHAVIOUR, type=int,
			description='Amount of live rankings to display (minimum: 15).',
			default=15
		)
		self.setting_nadeo_live_ranking = Setting(
			'nadeo_live_ranking', 'Show the Nadeo live rankings widget', Setting.CAT_BEHAVIOUR, type=bool,
			description='Show the Nadeo live rankings widgets besides the live rankings widget.', default=True,
			change_target=self.nadeo_widget_change
		)

	async def on_start(self):
		# Init settings.
		await self.context.setting.register(
			self.setting_rankings_amount, self.setting_nadeo_live_ranking
		)

		# Register signals
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)
		self.context.signals.listen(mp_signals.flow.round_start, self.round_start)
		self.context.signals.listen(tm_signals.finish, self.player_finish)
		self.context.signals.listen(tm_signals.waypoint, self.player_waypoint)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(tm_signals.give_up, self.player_giveup)
		self.context.signals.listen(tm_signals.scores, self.scores)
		self.context.signals.listen(tm_signals.warmup_start, self.warmup_start)
		self.context.signals.listen(tm_signals.warmup_end, self.warmup_end)


		# Make sure we move the multilap_info and disable the checkpoint_ranking and round_scores elements.
		if self.instance.game.game in ['tm', 'sm']:
			self.instance.ui_manager.properties.set_visibility('checkpoint_ranking', False)
			self.instance.ui_manager.properties.set_visibility('round_scores', await self.setting_nadeo_live_ranking.get_value())
			self.instance.ui_manager.properties.set_attribute('round_scores', 'pos', '-126.5 80. 150.')
			self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')

		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)

		self.widget = LiveRankingsWidget(self)
		await self.widget.display()

		scores = None
		try:
			scores = await self.instance.gbx('Trackmania.GetScores')
		except:
			pass

		if scores:
			await self.handle_scores(scores['players'])
			await self.widget.display()

		await self.get_points_repartition()

	async def nadeo_widget_change(self, *args, **kwargs):
		if self.instance.game.game in ['tm', 'sm']:
			self.instance.ui_manager.properties.set_visibility('round_scores', await self.setting_nadeo_live_ranking.get_value())
			await self.instance.ui_manager.properties.send_properties()

	def is_mode_supported(self, mode):
		mode = mode.lower()
		return mode.startswith('timeattack') or mode.startswith('rounds') or mode.startswith('team') or \
			   mode.startswith('laps') or mode.startswith('cup') or mode.startswith('trackmania/tm_timeattack_online') or \
			   mode.startswith('trackmania/tm_rounds_online') or mode.startswith('trackmania/tm_teams_online') or \
			   mode.startswith('trackmania/tm_laps_online') or mode.startswith('trackmania/tm_cup_online')

	async def scores(self, section, players, **kwargs):
		if section == 'PreEndRound':
			# Do not update the live rankings on the 'pre end round'-stage.
			# This will make the points added disappear without updating the actual scores.
			return

		await self.handle_scores(players)
		await self.widget.display()

	async def handle_scores(self, players):
		self.current_rankings = []
		self.current_finishes = []

		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'timeattack' in current_script or 'trackmania/tm_timeattack_online' in current_script:
			for player in players:
				if 'best_race_time' in player:
					if player['best_race_time'] != -1:
						new_ranking = dict(login=player['player'].login, nickname=player['player'].nickname, score=player['best_race_time'])
						self.current_rankings.append(new_ranking)
				elif 'bestracetime' in player:
					if player['bestracetime'] != -1:
						new_ranking = dict(login=player['login'], nickname=player['name'], score=player['bestracetime'])
						self.current_rankings.append(new_ranking)

			self.current_rankings.sort(key=lambda x: x['score'])
		elif 'rounds' in current_script or 'team' in current_script or 'cup' in current_script or \
			'trackmania/tm_rounds_online' in current_script or 'trackmania/tm_teams_online' in current_script or 'trackmania/tm_cup_online' in current_script:
			for player in players:
				if 'map_points' in player:
					if player['map_points'] != -1:
						new_ranking = dict(login=player['player'].login, nickname=player['player'].nickname, score=player['map_points'], points_added=0)
						self.current_rankings.append(new_ranking)
				elif 'mappoints' in player:
					if player['mappoints'] != -1:
						new_ranking = dict(login=player['login'], nickname=player['name'], score=player['mappoints'], points_added=0)
						self.current_rankings.append(new_ranking)

			self.current_rankings.sort(key=lambda x: x['score'])
			self.current_rankings.reverse()

	async def map_start(self, map, restarted, **kwargs):
		self.current_rankings = []
		self.current_finishes = []
		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)
		await self.get_points_repartition()
		await self.widget.display()

	async def round_start(self, count, time):
		await self.get_points_repartition()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.widget.display(player=player)

	async def warmup_start(self):
		self.current_rankings = []
		self.current_finishes = []
		await self.get_points_repartition()
		await self.widget.display()

	async def warmup_end(self):
		self.current_rankings = []
		self.current_finishes = []
		await self.get_points_repartition()
		await self.widget.display()

	async def player_giveup(self, time, player, flow):
		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'laps' not in current_script and 'trackmania/tm_laps_online' not in current_script:
			return

		current_rankings = [x for x in self.current_rankings if x['login'] == player.login]
		if len(current_rankings) > 0:
			current_ranking = current_rankings[0]
			current_ranking['giveup'] = True

		await self.widget.display()

	async def player_waypoint(self, player, race_time, flow, raw):
		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'laps' not in current_script and 'trackmania/tm_laps_online' not in current_script:
			return

		current_rankings = [x for x in self.current_rankings if x['login'] == player.login]
		if len(current_rankings) > 0:
			current_ranking = current_rankings[0]
			current_ranking['score'] = raw['racetime']
			current_ranking['cps'] = (raw['checkpointinrace'] + 1)
			current_ranking['best_cps'] = (self.current_rankings[0]['cps'])
			current_ranking['finish'] = raw['isendrace']
			current_ranking['cp_times'] = raw['curracecheckpoints']
			current_ranking['giveup'] = False
		else:
			best_cps = 0
			if len(self.current_rankings) > 0:
				best_cps = (self.current_rankings[0]['cps'])
			new_ranking = dict(login=player.login, nickname=player.nickname, score=raw['racetime'], cps=(raw['checkpointinrace'] + 1), best_cps=best_cps, cp_times=raw['curracecheckpoints'], finish=raw['isendrace'], giveup=False)
			self.current_rankings.append(new_ranking)

		self.current_rankings.sort(key=lambda x: (-x['cps'], x['score']))
		await self.widget.display()

	async def player_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'laps' in current_script or 'trackmania/tm_laps_online' in current_script:
			await self.player_waypoint(player, race_time, flow, raw)
			return

		if 'timeattack' in current_script or 'trackmania/tm_timeattack_online' in current_script:
			current_rankings = [x for x in self.current_rankings if x['login'] == player.login]
			score = lap_time
			if len(current_rankings) > 0:
				current_ranking = current_rankings[0]

				if score < current_ranking['score']:
					current_ranking['score'] = score
					self.current_rankings.sort(key=lambda x: x['score'])
					await self.widget.display()
			else:
				new_ranking = dict(login=player.login, nickname=player.nickname, score=score)
				self.current_rankings.append(new_ranking)
				self.current_rankings.sort(key=lambda x: x['score'])
				await self.widget.display()

			return

		if 'rounds' in current_script or 'team' in current_script or 'cup' in current_script or \
		'trackmania/tm_rounds_online' in current_script or 'trackmania/tm_teams_online' in current_script or 'trackmania/tm_cup_online' in current_script:

			new_finish = dict(login=player.login, nickname=player.nickname, score=race_time)
			self.current_finishes.append(new_finish)

			new_finish_rank = len(self.current_finishes) - 1
			new_finish['points_added'] = self.points_repartition[new_finish_rank] \
				if len(self.points_repartition) > new_finish_rank \
				else self.points_repartition[(len(self.points_repartition) - 1)]

			current_ranking = next((item for item in self.current_rankings if item['login'] == player.login), None)
			if current_ranking is not None:
				current_ranking['points_added'] = new_finish['points_added']
			else:
				new_finish['score'] = 0
				self.current_rankings.append(new_finish)

			self.current_rankings.sort(key=lambda x: (-x['score'], -x['points_added']))
			await self.widget.display()
			return

	async def get_points_repartition(self):
		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'rounds' in current_script or 'team' in current_script or 'cup' in current_script or \
		'trackmania/tm_rounds_online' in current_script or 'trackmania/tm_teams_online' in current_script or 'trackmania/tm_cup_online' in current_script:
			points_repartition = await self.instance.gbx('Trackmania.GetPointsRepartition')
			self.points_repartition = points_repartition['pointsrepartition']
		else:
			# Reset the points repartition array.
			self.points_repartition = []
			self.current_finishes = []
