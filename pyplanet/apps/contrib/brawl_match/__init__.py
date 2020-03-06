import asyncio
import random

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.brawl_match.views import (BrawlMapListView,
                                                     BrawlPlayerListView)
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.maniaplanet.models import Map, Player
from pyplanet.contrib.command import Command


class BrawlMatch(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	TIME_UNTIL_BAN_PHASE = 30
	TIME_UNTIL_MATCH_PHASE = 60
	TIME_UNTIL_NEXT_WALL = 3


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.ban_queue = asyncio.Queue()

		self.brawl_maps = [
			('26yU1ouud7IqURhbmlEzX3jxJM1', 49),  # On the Run
			('I5y9YjoVaw9updRFOecqmN0V6sh', 73),  # Moon Base
			('WUrcV1ziafkmDOEUQJslceNghs2', 72),  # Nos Astra
			('DPl6mjmUhXhlXqhpva_INcwvx5e', 55),  # Maru
			('3Pg4di6kaDyM04oHYm5AkC3r2ch', 46),  # Aliens Exist
			('ML4VsiZKZSiWNkwpEdSA11SH7mg', 51),  # L v g v s
			('GuIyeKb7lF6fsebOZ589d47Pqnk', 64)   # Only a wooden leg remained
		]
		self.match_maps = self.brawl_maps.copy()
		self.match_players = []
		self.chat_prefix = '$i$000.$903Brawl$fff - $z$fff'

		self.match_tasks = []
		self.backup_script_name = None
		self.backup_settings = None

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
			)
		)

	async def start_match_command(self, player, *args, **kwargs):
		if self.match_tasks:
			await self.brawl_chat(f'A match is currently in progress!', player)
		else:
			await self.register_match_task(self.start_match, player)

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
		await self.instance.map_manager.set_next_map(await Map.get_by_uid(self.match_maps[0][0]))

		await self.instance.gbx('NextMap')
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

		await self.instance.mode_manager.update_next_settings(settings)

	async def choose_players(self, player):
		player_view = BrawlPlayerListView(self)
		await player_view.display(player=player)

	async def add_player_to_match(self, admin, player_info):
		self.match_players.append(player_info['login'])
		message = f'Player {player_info["nickname"]}$z$fff is added to the match.'
		await self.brawl_chat(message, admin)

	async def start_ban_phase(self):
		event_loop = asyncio.get_running_loop()
		for player in self.match_players:
			event_loop.call_soon_threadsafe(self.ban_queue.put_nowait, player)

		nicks = [(await Player.get_by_login(player)).nickname for player in self.match_players]
		nicks_string = '$z$fff vs '.join(nicks)
		await self.brawl_chat(f'New match has been created: {nicks_string}$z$fff.')

		await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)
		await self.brawl_chat(f'Banning order:')
		for index, nick in enumerate(nicks, start=1):
			await self.brawl_chat(f'[{index}/{len(nicks)}] {nick}')

		await self.await_ban_phase()

		await self.next_ban()

	async def await_ban_phase(self):
		await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)
		await self.brawl_chat(f'Banning will start in {self.TIME_UNTIL_BAN_PHASE} seconds!')
		await asyncio.sleep(self.TIME_UNTIL_BAN_PHASE / 2)
		await self.brawl_chat(f'Banning will start in {int(self.TIME_UNTIL_BAN_PHASE/2)} seconds!')
		await asyncio.sleep(self.TIME_UNTIL_BAN_PHASE / 2)
		await self.brawl_chat(f'Banning will start now!')
		await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)

	async def next_ban(self):
		if len(self.match_maps) > 3:
			player_to_ban = await self.ban_queue.get()
			player_nick = (await Player.get_by_login(player_to_ban)).nickname
			message = f'[{self.match_players.index(player_to_ban)+1}/{len(self.match_players)}] {player_nick}$z$fff is now banning.'
			await self.brawl_chat(message)
			await self.ban_map(player_to_ban)
		else:
			maps_string = '$z$fff  -  '.join([(await Map.get_by_uid(map[0])).name for map in self.match_maps])
			await self.brawl_chat(f'Banning phase over! Maps for this match are:')
			await self.brawl_chat(f'{maps_string}')
			await self.init_match()

	async def ban_map(self, player):
		maps = [map[0] for map in self.match_maps]
		ban_view = BrawlMapListView(self, maps)
		await ban_view.display(player=player)

	async def remove_map_from_match(self, map_info):
		self.match_maps.pop(map_info['index']-1)

	async def init_match(self):
		await self.await_match_start()
		self.context.signals.listen(mp_signals.map.map_begin, self.set_settings_next_map)

		random.shuffle(self.match_maps)

		await self.brawl_chat(f'Map order: ')
		for index, (uid, _) in enumerate(self.match_maps, start=1):
			map_name = (await Map.get_by_uid(uid)).name
			await self.brawl_chat(f'[{index}/{len(self.match_maps)}] {map_name}')

		await self.set_match_settings()

	async def await_match_start(self):
		await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)
		await self.brawl_chat(f'Match will start in {self.TIME_UNTIL_MATCH_PHASE} seconds!')
		await asyncio.sleep(self.TIME_UNTIL_BAN_PHASE / 2)
		await self.brawl_chat(f'Match will start in {int(self.TIME_UNTIL_MATCH_PHASE/2)} seconds!')
		await asyncio.sleep(self.TIME_UNTIL_BAN_PHASE / 4)
		await self.brawl_chat(f'Match will start in {int(self.TIME_UNTIL_MATCH_PHASE/4)} seconds!')
		await asyncio.sleep(self.TIME_UNTIL_BAN_PHASE / 4)
		await self.brawl_chat(f'Match will start now!')
		await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)

	async def stop_match(self, player, *args, **kwargs):
		if not self.match_tasks:
			await self.brawl_chat(f'No match is currently in progress!', player)
			return
		for task in self.match_tasks:
			if not task.done():
				task.cancel()
		self.match_tasks = []
		await self.brawl_chat(f'Admin {player.nickname}$z$fff stopped match!')
		for signal, target in self.context.signals.listeners:
			if target == self.set_settings_next_map or target == self.set_settings:
				signal.unregister(target)
		self.match_maps = self.brawl_maps.copy()
		self.match_players = []

		await self.reset_backup()

	async def reset_backup(self):
		if not (self.backup_script_name and self.backup_settings):
			return
		await self.instance.mode_manager.set_next_script(self.backup_script_name)
		await self.instance.gbx('RestartMap')
		await self.instance.mode_manager.update_next_settings(self.backup_settings)

	async def update_finish_timeout(self, timeout):
		settings = await self.instance.mode_manager.get_settings()
		settings['S_FinishTimeout'] = timeout
		await self.instance.mode_manager.update_settings(settings)

	async def set_settings_next_map(self, map):
		settings = await self.instance.mode_manager.get_settings()
		for index, (uid, timeout) in enumerate(self.match_maps):
			if uid == map.uid:
				if index == len(self.match_maps) - 1 and settings['S_WarmUpNb'] == 1:
					settings['S_WarmUpNb'] = 0
					await self.instance.mode_manager.update_settings(settings)
				await self.update_finish_timeout(timeout)
				await self.instance.map_manager.set_next_map(
					await Map.get_by_uid(
						self.match_maps[(index + 1) % len(self.match_maps)][0]
					)
				)

	async def brawl_chat(self, message, player=None):
		if player:
			await self.instance.chat(f'{self.chat_prefix}{message}', player)
		else:
			await self.instance.chat(f'{self.chat_prefix}{message}')

	async def register_match_task(self, func, *args):
		self.match_tasks.append(asyncio.create_task(func(*args)))
