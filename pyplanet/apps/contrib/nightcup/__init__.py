import asyncio
from operator import itemgetter

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.nightcup.views import TimerView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.command import Command

class NightCup(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	TIME_UNTIL_TA_PHASE = 5 #int(0.25 * 60)
	TIME_UNTIL_KO_PHASE = 5 #int(0.5 * 60)
	TIME_AFTER_KO_PHASE = 5 #int(1 * 60)
	TIME_UNTIL_NEXT_WALL = 5 #3
	TIME_TA = int(2 * 60)


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.timeout = 60

		self.ta_finishers = []
		self.ko_qualified = []

		self.chat_reset = '$z$fff$s'
		self.chat_prefix = f'$fffRPG $036NIGHTCUP $fff- {self.chat_reset}'

		self.nc_active = False

		self.backup_script_name = None
		self.backup_settings = None

		self.open_views = []


	async def on_init(self):
		await super().on_init()


	async def on_start(self):
		# Registering permissions
		await self.instance.command_manager.register(
			Command(
				'start',
				namespace='nc',
				target=self.start_nc,
				admin=True
			),
			Command(
				'stop',
				namespace='nc',
				target=self.stop_nc,
				admin=True
			)
		)


	async def start_nc(self, player, *args, **kwargs):
		if self.nc_active:
			await self.nc_chat(f'A nightcup is currently in progress!', player)
		else:
			await self.nc_chat(f'Nightcup is starting now!')
			self.nc_active = True
			await self.backup_mode_settings()
			await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)
			await self.set_ta_settings()
			await self.await_match_start()
			await self.instance.gbx('RestartMap')
			self.context.signals.listen(mp_signals.map.map_begin, self.set_ko_settings)
			self.context.signals.listen(mp_signals.flow.round_end, self.get_qualified)


	async def backup_mode_settings(self):
		self.backup_script_name = await self.instance.mode_manager.get_current_full_script()
		self.backup_settings = await self.instance.mode_manager.get_settings()


	async def set_ta_settings(self):
		await self.instance.mode_manager.set_next_script('TimeAttack.Script.txt')

		await self.instance.gbx('RestartMap')
		while await self.instance.mode_manager.get_current_full_script() != 'TimeAttack.Script.txt':
			await asyncio.sleep(1)
		await self.set_ta_modesettings()


	async def set_ta_modesettings(self):
		settings = await self.instance.mode_manager.get_settings()

		settings['S_TimeLimit'] = self.TIME_TA
		settings['S_ChatTime'] = self.TIME_UNTIL_KO_PHASE

		await self.instance.mode_manager.update_settings(settings)


	async def await_match_start(self):
		match_start_timer = TimerView(self)
		self.open_views.append(match_start_timer)
		match_start_timer.title = f'TA phase starts in {await self.format_time(self.TIME_UNTIL_TA_PHASE)}'
		for player in self.instance.player_manager.online:
			await match_start_timer.display(player)

		for i in range(0, self.TIME_UNTIL_TA_PHASE):
			match_start_timer.title = f'TA phase starts in {await self.format_time(self.TIME_UNTIL_TA_PHASE - i)}'
			for player in self.instance.player_manager.online:
				await match_start_timer.display(player)
			await asyncio.sleep(1)

		await match_start_timer.destroy()


	async def format_time(self, seconds):
		return f'{seconds // 60}:{seconds % 60:02d}'


	async def stop_nc(self, player, *args, **kwargs):
		if not self.nc_active:
			await self.nc_chat(f'No nightcup is currently in progress!', player)
			return
		await self.nc_chat(f'Admin {player.nickname}{self.chat_reset} stopped nightcup!')
		await self.reset_server()


	async def reset_server(self):
		for view in self.open_views:
			await view.destroy()
		self.open_views.clear()

		for signal, target in self.context.signals.listeners:
			if target in [self.set_ko_settings, self.get_qualified, self.knockout_players, self.display_nr_of_kos]:
				signal.unregister(target)

		await self.reset_backup()


	async def reset_backup(self):
		if not (self.backup_script_name and self.backup_settings):
			return

		await asyncio.sleep(5)
		await self.instance.mode_manager.set_next_script(self.backup_script_name)
		await self.instance.mode_manager.update_next_settings(self.backup_settings)
		await self.instance.gbx('RestartMap')

		self.nc_active = False


	async def set_ko_settings(self, map):
		await self.instance.mode_manager.set_next_script('Rounds.Script.txt')

		await self.instance.gbx('RestartMap')
		while await self.instance.mode_manager.get_current_full_script() != 'Rounds.Script.txt':
			await asyncio.sleep(1)
		await self.set_ko_modesettings()

		for signal, target in self.context.signals.listeners:
			if target in [self.set_ko_settings, self.get_qualified]:
				signal.unregister(target)

		self.context.signals.listen(mp_signals.flow.round_end, self.knockout_players)
		self.context.signals.listen(mp_signals.flow.round_start, self.display_nr_of_kos)


	async def set_ko_modesettings(self):
		settings = await self.instance.mode_manager.get_settings()

		settings['S_PointsLimit'] = -1
		settings['S_RoundsPerMap'] = -1
		settings['S_WarmUpNb'] = 0
		settings['S_PointsRepartition'] = ','.join(str(x) for x in range(len(self.ko_qualified), 0, -1))
		settings['S_FinishTimeout'] = self.timeout
		settings['S_ChatTime'] = self.TIME_AFTER_KO_PHASE

		await self.instance.mode_manager.update_settings(settings)


	async def get_qualified(self, count, time):
		ta_results = (await self.instance.gbx('Trackmania.GetScores'))['players']
		self.ta_finishers = [record['login'] for record in ta_results if record['bestracetime'] != -1]
		self.ko_qualified = [p for (i,p) in enumerate(self.ta_finishers) if i < len(self.ta_finishers)/2]
		for p in self.instance.player_manager.online_logins:
			if p in self.ta_finishers:
				if p in self.ko_qualified:
					await self.nc_chat('Well done, you qualified for the KO phase!', p)
					await self.instance.gbx('ForceSpectator', p, 2)
				else:
					await self.nc_chat('Unlucky, you did not qualify for the KO phase!', p)
					await self.instance.gbx('ForceSpectator', p, 1)
			else:
				await self.instance.gbx('ForceSpectator', p, 1)


	async def knockout_players(self, count, time):
		nr_kos = await self.get_nr_kos(len(self.ko_qualified))
		round_scores = (await self.instance.gbx('Trackmania.GetScores'))['players']
		round_scores = [(record['login'], record['prevracetime']) for record in round_scores if record['login'] in self.ko_qualified]

		round_scores.sort(key=itemgetter(1))
		round_scores = [p for p in round_scores if p[1] != -1]
		if len(round_scores) == 0:
			return

		round_logins = [p[0] for p in round_scores]

		if len(self.ko_qualified) == 2:
			await self.nc_chat(f'Player {(await Player.get_by_login(round_scores[0][0])).nickname}{self.chat_reset} wins this RPG NightCup, well played!')
			await self.reset_server()
			return

		dnfs = [p for p in self.ko_qualified if p not in round_logins]
		kos = round_logins[len(self.ko_qualified)-nr_kos:]
		qualified = round_logins[:len(self.ko_qualified)-nr_kos]
		for i,p in enumerate(kos, start=1):
			await self.nc_chat(f'You have been eliminated from this KO: position {len(qualified) + i}/{len(self.ko_qualified)}', p)
			await self.instance.gbx('ForceSpectator', p, 1)
		for p in dnfs:
			await self.nc_chat(f'You have been eliminated from this KO: position DNF/{len(self.ko_qualified)}', p)
			await self.instance.gbx('ForceSpectator', p, 1)
		for i,p in enumerate(qualified, start=1):
			await self.nc_chat(f'You are still in! position {i}/{len(self.ko_qualified)}', p)
			await self.instance.gbx('ForceSpectator', p, 2)

		kos.extend(dnfs)
		kos = [(await Player.get_by_login(login)).nickname for login in kos]
		kos_string = f'{self.chat_reset}, '.join(kos)
		await self.nc_chat(f'Players knocked out: {kos_string}')

		self.ko_qualified = [p for p in self.ko_qualified if p in qualified]


	async def display_nr_of_kos(self, count, time):
		await self.nc_chat(f'{len(self.ko_qualified)} players left, number of KOs: {await self.get_nr_kos(len(self.ko_qualified))}')


	async def get_nr_kos(self, nr_players):
		return int((nr_players + 4) / 10) + 1


	async def nc_chat(self, message, player=None):
		if player:
			await self.instance.chat(f'{self.chat_prefix}{message}', player)
		else:
			await self.instance.chat(f'{self.chat_prefix}{message}')
