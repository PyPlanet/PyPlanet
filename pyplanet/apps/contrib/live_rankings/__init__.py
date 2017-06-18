from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.live_rankings.views import LiveRankingsWidget

from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class LiveRankings(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_rankings = []
		self.widget = None

	async def on_start(self):
		# Register signals
		self.instance.signal_manager.listen(mp_signals.map.map_start, self.map_start)
		self.instance.signal_manager.listen(tm_signals.finish, self.player_finish)
		self.instance.signal_manager.listen(tm_signals.waypoint, self.player_waypoint)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)
		self.instance.signal_manager.listen(tm_signals.give_up, self.player_giveup)
		self.instance.signal_manager.listen(tm_signals.scores, self.scores)

		# Make sure we move the rounds_scores and other gui elements.
		self.instance.ui_manager.properties.set_attribute('round_scores', 'pos', '-126.5 87. 150.')
		self.instance.ui_manager.properties.set_visibility('checkpoint_ranking', False)
		self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')

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

	def is_mode_supported(self, mode):
		mode = mode.lower()
		return mode.startswith('timeattack') or mode.startswith('rounds') or mode.startswith('team') or \
			   mode.startswith('laps') or mode.startswith('cup')

	async def scores(self, section, players, **kwargs):
		await self.handle_scores(players)
		await self.widget.display()

	async def handle_scores(self, players):
		self.current_rankings = []

		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'timeattack' in current_script:
			for player in players:
				if 'best_race_time' in player:
					if player['best_race_time'] != -1:
						new_ranking = dict(nickname=player['player'].nickname, score=player['best_race_time'])
						self.current_rankings.append(new_ranking)
				elif 'bestracetime' in player:
					if player['bestracetime'] != -1:
						new_ranking = dict(nickname=player['name'], score=player['bestracetime'])
						self.current_rankings.append(new_ranking)

			self.current_rankings.sort(key=lambda x: x['score'])
		elif 'rounds' in current_script or 'team' in current_script or 'cup' in current_script:
			for player in players:
				if 'map_points' in player:
					if player['map_points'] != -1:
						new_ranking = dict(nickname=player['player'].nickname, score=player['map_points'])
						self.current_rankings.append(new_ranking)
				elif 'mappoints' in player:
					if player['mappoints'] != -1:
						new_ranking = dict(nickname=player['name'], score=player['mappoints'])
						self.current_rankings.append(new_ranking)

			self.current_rankings.sort(key=lambda x: x['score'])
			self.current_rankings.reverse()

	async def map_start(self, map, restarted, **kwargs):
		self.current_rankings = []
		await self.widget.display()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.widget.display(player=player)

	async def player_giveup(self, time, player, flow):
		if 'Laps' not in await self.instance.mode_manager.get_current_script():
			return

		current_rankings = [x for x in self.current_rankings if x['nickname'] == player.nickname]
		if len(current_rankings) > 0:
			current_ranking = current_rankings[0]
			current_ranking['giveup'] = True

		await self.widget.display()

	async def player_waypoint(self, player, race_time, flow, raw):
		if 'laps' not in (await self.instance.mode_manager.get_current_script()).lower():
			return

		current_rankings = [x for x in self.current_rankings if x['nickname'] == player.nickname]
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
			new_ranking = dict(nickname=player.nickname, score=raw['racetime'], cps=(raw['checkpointinrace'] + 1), best_cps=best_cps, cp_times=raw['curracecheckpoints'], finish=raw['isendrace'], giveup=False)
			self.current_rankings.append(new_ranking)

		self.current_rankings.sort(key=lambda x: (-x['cps'], x['score']))
		await self.widget.display()

	async def player_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		current_script = (await self.instance.mode_manager.get_current_script()).lower()
		if 'laps' in current_script:
			await self.player_waypoint(player, race_time, flow, raw)
			return

		if 'timeattack' not in current_script:
			return

		current_rankings = [x for x in self.current_rankings if x['nickname'] == player.nickname]
		score = lap_time
		if len(current_rankings) > 0:
			current_ranking = current_rankings[0]

			if score < current_ranking['score']:
				current_ranking['score'] = score
				self.current_rankings.sort(key=lambda x: x['score'])
				await self.widget.display()
		else:
			new_ranking = dict(nickname=player.nickname, score=score)
			self.current_rankings.append(new_ranking)
			self.current_rankings.sort(key=lambda x: x['score'])
			await self.widget.display()
