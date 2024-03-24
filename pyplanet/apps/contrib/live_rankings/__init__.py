import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.live_rankings.views import LiveRankingsWidget, RaceRankingsWidget

from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from pyplanet.contrib.setting import Setting


class LiveRankings(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.finish_lock = asyncio.Lock()
		self.current_rankings = []
		self.points_repartition = []
		self.current_finishes = []
		self.is_warming_up = False
		self.widget = None
		self.dedimania_enabled = False

		self.race_widget = None
		self.display_race_widget = False

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
		self.setting_race_ranking = Setting(
			'race_live_ranking', 'Show the race rankings widget', Setting.CAT_BEHAVIOUR, type=bool,
			description='Show the race rankings widgets besides the live rankings widget.', default=True,
			change_target=self.race_widget_change
		)

	async def on_start(self):
		# Init settings.
		if self.instance.game.game == 'tmnext':
			self.setting_nadeo_live_ranking.default = False

		await self.context.setting.register(
			self.setting_rankings_amount, self.setting_nadeo_live_ranking, self.setting_race_ranking
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
		self.context.signals.listen(tm_signals.warmup_start_round, self.warmup_start)
		self.context.signals.listen(tm_signals.warmup_end, self.warmup_end)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)

		# Make sure we move the multilap_info and disable the checkpoint_ranking and round_scores elements.
		if self.instance.game.game in ['tm', 'sm']:
			self.instance.ui_manager.properties.set_visibility('checkpoint_ranking', False)
			self.instance.ui_manager.properties.set_visibility('round_scores',
															   await self.setting_nadeo_live_ranking.get_value())
			self.instance.ui_manager.properties.set_attribute('round_scores', 'pos', '-126.5 80. 150.')
			self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')
		else:
			self.instance.ui_manager.properties.set_visibility('Rounds_SmallScoresTable',
															   await self.setting_nadeo_live_ranking.get_value())
			await self.instance.ui_manager.properties.send_properties()

		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)

		self.widget = LiveRankingsWidget(self)
		await self.widget.display()

		# Create the race rankings widget, call setting change method to set the UI accordingly.
		self.race_widget = RaceRankingsWidget(self)
		await self.race_widget_change(self)

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
			self.instance.ui_manager.properties.set_visibility('round_scores',
															   await self.setting_nadeo_live_ranking.get_value())
			await self.instance.ui_manager.properties.send_properties()
		else:
			self.instance.ui_manager.properties.set_visibility('Rounds_SmallScoresTable',
															   await self.setting_nadeo_live_ranking.get_value())
			await self.instance.ui_manager.properties.send_properties()

	async def race_widget_change(self, *args, **kwargs):
		self.display_race_widget = await self.setting_race_ranking.get_value()
		if not self.display_race_widget:
			await self.race_widget.hide()

		# Hide the game-provided race rankings widget when displaying this one.
		# Otherwise, reset visibility to the Nadeo live ranking setting.
		if self.instance.game.game in ['tm', 'sm']:
			if self.display_race_widget is True:
				self.instance.ui_manager.properties.set_visibility('round_scores', False)
				await self.instance.ui_manager.properties.send_properties()
			else:
				self.instance.ui_manager.properties.set_visibility('round_scores', await self.setting_nadeo_live_ranking.get_value())
				await self.instance.ui_manager.properties.send_properties()
		else:
			if self.display_race_widget is True:
				self.instance.ui_manager.properties.set_visibility('Rounds_SmallScoresTable', False)
				await self.instance.ui_manager.properties.send_properties()
			else:
				self.instance.ui_manager.properties.set_visibility(
					'Rounds_SmallScoresTable',
					(await self.setting_nadeo_live_ranking.get_value()) or (await self.setting_race_ranking.get_value())
				)
				await self.instance.ui_manager.properties.send_properties()

	def is_mode_rounds(self, mode):
		mode = mode.lower()
		return any(['rounds' in mode, 'team' in mode, 'cup' in mode, 'trackmania/tm_rounds_online' in mode,
					'trackmania/tm_teams_online' in mode, 'trackmania/tm_cup_online' in mode,
					mode == 'turborounds', mode == 'keklrounds2', mode == 'tm_roundskekl_online'])

	def is_mode_ta(self, mode):
		mode = mode.lower()
		return any(['timeattack' in mode, 'trackmania/tm_timeattack_online' in mode])

	def is_mode_supported(self, mode):
		mode = mode.lower()
		return any([
			mode == 'turborounds', mode == 'keklrounds2', mode == 'tm_roundskekl_online',
			mode.startswith('timeattack'), mode.startswith('rounds'), mode.startswith('team'),
			mode.startswith('laps'), mode.startswith('cup'), mode.startswith('trackmania/tm_timeattack_online'),
			mode.startswith('trackmania/tm_rounds_online'), mode.startswith('trackmania/tm_teams_online'),
			mode.startswith('trackmania/tm_laps_online'), mode.startswith('trackmania/tm_cup_online')
		])

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
		if self.is_mode_ta(current_script):
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
		elif self.is_mode_rounds(current_script):
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

	async def round_start(self, count, time, valid=None):
		await self.get_points_repartition()
		await self.race_widget.hide()

	async def podium_start(self, **kwargs):
		await self.race_widget.hide()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.widget.display(player=player)

	async def warmup_start(self, **kwargs):
		self.is_warming_up = True
		self.current_rankings = []
		self.current_finishes = []
		await self.get_points_repartition()
		await self.widget.display()
		await self.race_widget.hide()

	async def warmup_end(self, **kwargs):
		self.is_warming_up = False
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

	async def player_finish(self, player, race_time, lap_time, cps, flow, is_end_race, raw, **kwargs):
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
			if not is_end_race:
				# The finish event is also triggered when passing the finish in a multi-lap map, while not finishing the map.
				# In that case, no results should be processed as the player hasn't actually finished.
				return

			append_finish = True
			if self.is_warming_up:
				# During the warm-up, players can finish multiple times - only display the best time.
				current_finishes = [x for x in self.current_finishes if x['login'] == player.login]
				if len(current_finishes) > 0:
					if race_time < current_finishes[0]['score']:
						current_finishes[0]['score'] = race_time
					append_finish = False

			new_finish = dict(login=player.login, nickname=player.nickname, score=race_time, points_added=0)
			if append_finish:
				self.current_finishes.append(new_finish)
			self.current_finishes.sort(key=lambda x: (x['score']))

			async with self.finish_lock:
				if not self.is_warming_up:
					# Always iterate through all current finishes on adding a new finish.
					# Because of latency, the finish event might not fire in the correct order based on the scores.
					for finish_rank, current_finish in enumerate(self.current_finishes):
						current_finish['points_added'] = self.points_repartition[finish_rank] \
							if len(self.points_repartition) > finish_rank \
							else self.points_repartition[(len(self.points_repartition) - 1)]

						current_ranking = next((item for item in self.current_rankings if item['login'] == current_finish['login']), None)
						if current_ranking is not None:
							current_ranking['points_added'] = current_finish['points_added']
						else:
							new_ranking = dict(login=current_finish['login'], nickname=current_finish['nickname'], score=0, points_added=current_finish['points_added'])
							self.current_rankings.append(new_ranking)

					self.current_rankings.sort(key=lambda x: (-x['score'], -x['points_added']))
					await self.widget.display()

				if self.display_race_widget:
					await self.race_widget.display()
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
