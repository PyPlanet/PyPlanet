import asyncio
import random
import collections

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.brawl_match.views import (BrawlMapListView,
													 BrawlPlayerListView,
													 TimerView)
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.maniaplanet.models import Map, Player
from pyplanet.contrib.command import Command


class BrawlMatch(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	TIME_UNTIL_BAN_PHASE = 30
	TIME_UNTIL_MATCH_PHASE = 60
	TIME_UNTIL_NEXT_WALL = 3
	TIME_BREAK = 120


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ban_queue = asyncio.Queue()

		self.brawl_maps = [
			'26yU1ouud7IqURhbmlEzX3jxJM1',  # On the Run
			'I5y9YjoVaw9updRFOecqmN0V6sh',  # Moon Base
			'WUrcV1ziafkmDOEUQJslceNghs2',  # Nos Astra
			'DPl6mjmUhXhlXqhpva_INcwvx5e',  # Maru
			'3Pg4di6kaDyM04oHYm5AkC3r2ch',  # Aliens Exist
			'ML4VsiZKZSiWNkwpEdSA11SH7mg',  # L v g v s
			'GuIyeKb7lF6fsebOZ589d47Pqnk'   # Only a wooden leg remained
		]
		self.timeouts = {
			'26yU1ouud7IqURhbmlEzX3jxJM1': 49,  # On the Run
			'I5y9YjoVaw9updRFOecqmN0V6sh': 73,  # Moon Base
			'WUrcV1ziafkmDOEUQJslceNghs2': 72,  # Nos Astra
			'DPl6mjmUhXhlXqhpva_INcwvx5e': 55,  # Maru
			'3Pg4di6kaDyM04oHYm5AkC3r2ch': 46,  # Aliens Exist
			'ML4VsiZKZSiWNkwpEdSA11SH7mg': 61,  # L v g v s
			'GuIyeKb7lF6fsebOZ589d47Pqnk': 64   # Only a wooden leg remained
		}

		self.match_maps = collections.deque(self.brawl_maps)
		self.match_players = []
		self.ready_players = []
		self.endwu_voted_players = []
		self.requested_break_players = []
		self.break_queued = False
		self.chat_reset = '$z$fff$s'
		self.chat_prefix = f'$i$000.$903Brawl$fff - {self.chat_reset}'

		self.match_tasks = []
		self.match_active = False
		self.backup_script_name = None
		self.backup_settings = None
		self.maps_played = 0
		self.rounds_played = 0
		self.open_views = []

	async def on_init(self):
		await super().on_init()

	async def on_start(self):
		# Registering permissions
		await self.instance.permission_manager.register(
			'match_control',
			'Starting/Stopping brawl matches',
			app=self,
			min_level=2
		)

		# Registering commands
		await self.instance.command_manager.register(
			Command(
				'start',
				namespace='match',
				target=self.start_match_command,
				perms='brawl_match:match_control',
				admin=True
			),
			Command(
				'stop',
				namespace='match',
				target=self.stop_match,
				perms='brawl_match:match_control',
				admin=True
			),
			Command(
				'ready',
				aliases=['r'],
				namespace='match',
				target=self.player_ready
			),
			Command(
				'endwu',
				namespace='match',
				target=self.vote_endwu
			),
			Command(
				'break',
				namespace='match',
				target=self.request_break
			)
		)

	async def start_match_command(self, player, *args, **kwargs):
		if self.match_tasks:
			await self.brawl_chat(f'A match is currently in progress!', player)
		elif not await self.check_maps_on_server():
			await self.brawl_chat(f'Not all maps for the match are on the server', player)
		else:
			await self.register_match_task(self.start_match, player)

	async def check_maps_on_server(self):
		return all([self.instance.map_manager.playlist_has_map(map) for map in self.brawl_maps])

	async def start_match(self, player):
		message = f'You started a brawl match. Pick the participants from worst to best seed.'
		await self.brawl_chat(message, player)

		await self.backup_mode_settings()

		await self.choose_players(player=player)

	async def backup_mode_settings(self):
		self.backup_script_name = await self.instance.mode_manager.get_current_full_script()
		self.backup_settings = await self.instance.mode_manager.get_settings()

	async def set_match_settings(self):
		await self.instance.mode_manager.set_next_script('Cup.Script.txt')
		await self.instance.map_manager.set_next_map(await Map.get_by_uid(self.match_maps[0]))

		await self.instance.gbx('NextMap')
		while await self.instance.mode_manager.get_current_full_script() != 'Cup.Script.txt':
			await asyncio.sleep(1)
		await self.set_settings()

	async def set_settings(self):
		settings = await self.instance.mode_manager.get_settings()

		settings['S_AllowRespawn'] = True
		settings['S_NbOfPlayersMax'] = 4
		settings['S_NbOfPlayersMin'] = 2
		settings['S_NbOfWinners'] = 2
		settings['S_PointsLimit'] = 70
		settings['S_PointsRepartition'] = '10,6,4,3'
		settings['S_RoundsPerMap'] = 3
		settings['S_WarmUpNb'] = 1
		settings['S_WarmUpDuration'] = -1

		await self.instance.mode_manager.update_settings(settings)

	async def choose_players(self, player):
		player_view = BrawlPlayerListView(self)
		self.open_views.append(player_view)
		await player_view.display(player=player)

	async def add_player_to_match(self, admin, player_info):
		self.match_players.append(await Player.get_by_login(player_info['login']))
		message = f'Player {player_info["nickname"]}{self.chat_reset} is added to the match.'
		await self.brawl_chat(message, admin)

	async def force_player_and_spectator(self):
		for player in self.instance.player_manager.online:
			if player in self.match_players:
				await self.instance.gbx('ForceSpectator', player.login, 2)
			else:
				await self.instance.gbx('ForceSpectator', player.login, 1)

	async def start_ready_phase(self):
		nicks = [player.nickname for player in self.match_players]
		nicks_string = f'{self.chat_reset} vs '.join(nicks)
		await self.brawl_chat(f'New match has been created: {nicks_string}{self.chat_reset}.')
		self.match_active = True
		await self.brawl_chat('Some general information:')
		await self.brawl_chat('First rotation will have warmups, after that warmup is disabled')
		await self.brawl_chat('You can vote to skip the warmup using /match endwu')
		await self.brawl_chat('You are allowed 1 break, request it by using /match break')
		await self.brawl_chat('To start the match, type /match r')

	async def start_ban_phase(self):
		event_loop = asyncio.get_running_loop()
		for player in self.match_players:
			event_loop.call_soon_threadsafe(self.ban_queue.put_nowait, player)

		nicks = [player.nickname for player in self.match_players]

		await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)
		await self.brawl_chat(f'Banning order:')
		for index, nick in enumerate(nicks, start=1):
			await self.brawl_chat(f'[{index}/{len(nicks)}] {nick}')

		await self.await_ban_phase()

		await self.next_ban()

	async def await_ban_phase(self):
		ban_start_timer = TimerView(self)
		self.open_views.append(ban_start_timer)
		ban_start_timer.title = f'Banning starts in {await self.format_time(self.TIME_UNTIL_BAN_PHASE)}'
		for player in self.instance.player_manager.online:
			await ban_start_timer.display(player)

		for i in range(0, self.TIME_UNTIL_BAN_PHASE):
			ban_start_timer.title = f'Banning starts in {await self.format_time(self.TIME_UNTIL_BAN_PHASE - i)}'
			for player in self.instance.player_manager.online:
				await ban_start_timer.display(player)
			await asyncio.sleep(1)

		await ban_start_timer.destroy()

	async def next_ban(self):
		if len(self.match_maps) > 3:
			player_to_ban = await self.ban_queue.get()
			player_nick = player_to_ban.nickname
			message = f'[{self.match_players.index(player_to_ban)+1}/{len(self.match_players)}] {player_nick}{self.chat_reset} is now banning.'
			await self.brawl_chat(message)
			await self.ban_map(player_to_ban)
			self.ban_queue.task_done()
		else:
			maps_string = f'{self.chat_reset}  -  '.join([(await Map.get_by_uid(map)).name for map in self.match_maps])
			await self.brawl_chat(f'Banning phase over! Maps for this match are:')
			await self.brawl_chat(f'{maps_string}')
			await self.init_match()

	async def ban_map(self, player):
		ban_view = BrawlMapListView(self, self.match_maps)
		self.open_views.append(ban_view)
		await ban_view.display(player=player)

	async def remove_map_from_match(self, player, map_info):
		await self.brawl_chat(f'Player '
								  f'{player.nickname}{self.chat_reset} has just banned '
								  f'{map_info["name"]}')
		del self.match_maps[map_info['index']-1]

	async def init_match(self):
		await self.await_match_start()
		self.context.signals.listen(mp_signals.map.map_begin, self.set_settings_next_map)
		self.context.signals.listen(mp_signals.flow.round_start, self.display_current_round)
		self.context.signals.listen(mp_signals.flow.round_end, self.incr_round_counter)
		self.context.signals.listen(mp_signals.flow.match_end__end, self.reset_server)

		random.shuffle(self.match_maps)

		await self.set_match_settings()

	async def display_map_order(self):
		await self.brawl_chat(f'Upcoming maps: ')
		for index, uid in enumerate(self.match_maps, start=1):
			map_name = (await Map.get_by_uid(uid)).name
			await self.brawl_chat(f'[{index}/{len(self.match_maps)}] {map_name}')
		await self.check_for_wu_messages()

	async def check_for_wu_messages(self):
		if self.maps_played == len(self.match_maps) - 1:
			await self.brawl_chat('$oNo more warmup in future!')
		elif self.maps_played == len(self.match_maps):
			await self.remove_wu()
			await self.brawl_chat('$oWarmup is disabled!')

	async def await_match_start(self):
		match_start_timer = TimerView(self)
		self.open_views.append(match_start_timer)
		match_start_timer.title = f'Match starts in {await self.format_time(self.TIME_UNTIL_MATCH_PHASE)}'
		for player in self.instance.player_manager.online:
			await match_start_timer.display(player)

		for i in range(0, self.TIME_UNTIL_MATCH_PHASE):
			match_start_timer.title = f'Match starts in {await self.format_time(self.TIME_UNTIL_MATCH_PHASE - i)}'
			for player in self.instance.player_manager.online:
				await match_start_timer.display(player)
			await asyncio.sleep(1)

		await match_start_timer.destroy()

	async def stop_match(self, player, *args, **kwargs):
		if not self.match_tasks:
			await self.brawl_chat(f'No match is currently in progress!', player)
			return
		self.match_active = False
		await self.brawl_chat(f'Admin {player.nickname}{self.chat_reset} stopped match!')
		await self.reset_server()

	async def reset_server(self, count=0, time=0):
		for task in self.match_tasks:
			if not task.done():
				task.cancel()
		self.match_tasks.clear()

		for view in self.open_views:
			await view.destroy()

		for signal, target in self.context.signals.listeners:
			if target in [self.set_settings_next_map, self.display_current_round,
						self.incr_round_counter, self.reset_server,
						  self.init_break]:
				signal.unregister(target)

		self.maps_played = 0

		self.match_maps = collections.deque(self.brawl_maps)
		self.match_players.clear()
		self.ready_players.clear()
		self.endwu_voted_players.clear()
		self.requested_break_players.clear()

		while not self.ban_queue.empty():
			await self.ban_queue.get()
			self.ban_queue.task_done()

		await self.reset_backup()

	async def reset_backup(self):
		if not (self.backup_script_name and self.backup_settings):
			return

		await asyncio.sleep(5)
		await self.instance.mode_manager.set_next_script(self.backup_script_name)
		await self.instance.mode_manager.update_next_settings(self.backup_settings)
		await self.instance.gbx('RestartMap')

	async def update_finish_timeout(self, timeout):
		settings = await self.instance.mode_manager.get_settings()
		settings['S_FinishTimeout'] = timeout
		await self.instance.mode_manager.update_settings(settings)

	async def set_settings_next_map(self, map):
		if self.maps_played == len(self.match_maps):
			await self.remove_wu()

		await self.update_finish_timeout(self.timeouts[self.match_maps[0]])
		await self.instance.map_manager.set_next_map(
			await Map.get_by_uid(
				self.match_maps[1]
			)
		)

		await self.display_map_order()
		self.match_maps.rotate(-1)
		self.maps_played += 1
		self.rounds_played = 0
		self.endwu_voted_players.clear()
		if (await self.instance.mode_manager.get_settings())['S_WarmUpNb'] > 0:
			await self.brawl_chat(f"It's possible to vote to end the warmup by using /match endwu")

	async def incr_round_counter(self, count, time):
		if await self.finishers():
			self.rounds_played += 1

	async def finishers(self):
		players = (await self.instance.gbx('Trackmania.GetScores'))['players']
		return any([player['roundpoints'] != 0 for player in players])

	async def display_current_round(self, count, time):
		rounds_per_map = (await self.instance.mode_manager.get_settings())['S_RoundsPerMap']
		await self.brawl_chat(f'Round {self.rounds_played+1}/{rounds_per_map}')

	async def remove_wu(self):
		settings = await self.instance.mode_manager.get_settings()
		settings['S_WarmUpNb'] = 0
		await self.instance.mode_manager.update_settings(settings)

	async def player_ready(self, player, data, *args, **kwargs):
		if not self.match_active:
			await self.brawl_chat('There is no match in progress.', player)
		elif player not in self.match_players:
			await self.brawl_chat('You are not a participant in the ongoing match.', player)
		elif player in self.ready_players:
			await self.brawl_chat(f'You are ready.')
		else:
			self.ready_players.append(player)
			await self.brawl_chat(f'Player {player.nickname}{self.chat_reset} is ready!')
			if set(self.match_players) == set(self.ready_players):
				await self.brawl_chat('Everyone is ready. Match is starting.')
				await self.start_ban_phase()

	async def vote_endwu(self, player, data, *args, **kwargs):
		if not self.match_active:
			await self.brawl_chat('There is no match in progress.', player)
		elif player not in self.match_players:
			await self.brawl_chat('You are not a participant in the ongoing match.', player)
		elif not (await self.instance.gbx('Trackmania.WarmUp.GetStatus'))['active']:
			await self.brawl_chat('No warmup in progress.', player)
		elif player in self.endwu_voted_players:
			await self.brawl_chat('You have already voted to skip the warmup.', player)
		else:
			self.endwu_voted_players.append(player)
			await self.brawl_chat(f'Player {player.nickname}{self.chat_reset} has voted to end the warmup!')
			if set(self.match_players) == set(self.endwu_voted_players):
				await self.instance.gbx('Trackmania.WarmUp.ForceStop', encode_json=False, response_id=False)

	async def request_break(self, player, data, *args, **kwargs):
		if not self.match_active:
			await self.brawl_chat('There is no match in progress.', player)
		elif player not in self.match_players:
			await self.brawl_chat('You are not a participant in the ongoing match.', player)
		elif player in self.requested_break_players:
			await self.brawl_chat('You have already requested your break.', player)
		elif self.break_queued:
			await self.brawl_chat('There is already a break planned. You can request a break again during that break.', player)
		else:
			self.break_queued = True
			self.requested_break_players.append(player)
			await self.brawl_chat(f'Player {player.nickname}{self.chat_reset} has requested their break!')
			self.context.signals.listen(mp_signals.flow.round_start, self.init_break)

	async def init_break(self, count, time):
		for signal, target in self.context.signals.listeners:
			if target == self.init_break:
				signal.unregister(target)
		self.break_queued = False

		await self.register_match_task(self.await_break)

	async def await_break(self):
		break_timer = TimerView(self)
		self.open_views.append(break_timer)
		break_timer.title = f'Break ends in {await self.format_time(self.TIME_BREAK)}'
		for player in self.instance.player_manager.online:
			await break_timer.display(player)

		for i in range(0, self.TIME_BREAK):
			break_timer.title = f'Break ends in {await self.format_time(self.TIME_BREAK - i)}'
			for player in self.instance.player_manager.online:
				await break_timer.display(player)
			await asyncio.sleep(1)

		await break_timer.destroy()
		await self.instance.gbx('Trackmania.ForceEndRound', encode_json=False, response_id=False)

	async def format_time(self, seconds):
		return f'{seconds // 60}:{seconds % 60:02d}'

	async def brawl_chat(self, message, player=None):
		if player:
			await self.instance.chat(f'{self.chat_prefix}{message}', player)
		else:
			await self.instance.chat(f'{self.chat_prefix}{message}')

	async def register_match_task(self, func, *args):
		self.match_tasks.append(asyncio.create_task(func(*args)))
