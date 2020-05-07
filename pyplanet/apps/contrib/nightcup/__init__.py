import asyncio
from operator import itemgetter

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.nightcup.views import TimerView, SettingsListView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.command import Command

class NightCup(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	TIME_UNTIL_NEXT_WALL = 3

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.timeout = 60

		self.ta_finishers = []
		self.ko_qualified = []

		self.settings_long = [
			{
				'default': '60',
				'type': int,
				'name': 'nc_time_until_ta',
				'description': 'Time before TA phase starts',
				'value': 60
			},
			{
				'default': '2700',
				'type': int,
				'name': 'nc_ta_length',
				'description': 'Length of TA phase',
				'value': 2700
			},
			{
				'default': '600',
				'type': int,
				'name': 'nc_time_until_ko',
				'description': 'Time between TA phase and KO phase',
				'value': 600
			},
			{
				'default': '60',
				'type': int,
				'name': 'nc_wu_duration',
				'description': 'Length of warmups for players to load the map',
				'value': 60
			}
		]

		self.settings = {setting['name']: setting['value'] for setting in self.settings_long}
		self.chat_reset = '$z$fff$s'
		self.chat_prefix = f'$fffRPG $036NIGHTCUP $fff- {self.chat_reset}'

		self.nc_active = False

		self.backup_script_name = None
		self.backup_settings = None

		self.open_views = []


	async def on_init(self):
		await super().on_init()


	async def on_start(self):
		await self.instance.permission_manager.register(
			'nc_control',
			'Starting/Stopping nightcups',
			app=self,
			min_level=2
		)

		await self.instance.command_manager.register(
			Command(
				'start',
				namespace='nc',
				target=self.start_nc,
				perms='nightcup:nc_control',
				admin=True
			),
			Command(
				'stop',
				namespace='nc',
				target=self.stop_nc,
				perms='nightcup:nc_control',
				admin=True
			),
			Command(
				'settings',
				namespace='nc',
				target=self.nc_settings,
				perms='nightcup:nc_control',
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
			await self.await_match_start()


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

		settings['S_TimeLimit'] = self.settings['nc_ta_length']
		settings['S_WarmUpDuration'] = self.settings['nc_wu_duration']
		settings['S_WarmUpNb'] = 1
		await self.instance.mode_manager.update_settings(settings)

		await self.nc_chat(f"Warmup of {await self.format_time(self.settings['nc_wu_duration'])} for people to load the map.")


	async def await_match_start(self):
		match_start_timer = TimerView(self)
		self.open_views.append(match_start_timer)
		match_start_timer.title = f"TA phase starts in {await self.format_time(self.settings['nc_time_until_ta'])}"
		for player in self.instance.player_manager.online:
			await match_start_timer.display(player)

		for i in range(0, self.settings['nc_time_until_ta']):
			match_start_timer.title = f"TA phase starts in {await self.format_time(self.settings['nc_time_until_ta'] - i)}"
			for player in self.instance.player_manager.online:
				if match_start_timer:
					await match_start_timer.display(player)
			await asyncio.sleep(1)

		await match_start_timer.destroy()
		await self.instance.gbx('RestartMap')

		await self.set_ta_settings()
		self.context.signals.listen(mp_signals.flow.round_end, self.get_qualified)
		self.context.signals.listen(mp_signals.flow.round_end, self.await_ko_start)


	async def await_ko_start(self, count, time):
		settings = await self.instance.mode_manager.get_settings()
		settings['S_TimeLimit'] = -1
		settings['S_WarmUpDuration'] = 0
		settings['S_WarmUpNb'] = -1
		await self.instance.mode_manager.update_settings(settings)

		for signal, target in self.context.signals.listeners:
			if target == self.await_ko_start:
				signal.unregister(target)

		await self.instance.gbx('RestartMap')

		self.context.signals.listen(mp_signals.map.map_begin, self.set_ko_settings)
		ko_start_timer = TimerView(self)
		self.open_views.append(ko_start_timer)
		ko_start_timer.title = f"KO phase starts in {await self.format_time(settings['nc_time_until_ko'])}"
		for player in self.instance.player_manager.online:
			await ko_start_timer.display(player)

		for i in range(0, settings['nc_time_until_ko']):
			ko_start_timer.title = f"KO phase starts in {await self.format_time(settings['nc_time_until_ko'])}"
			for player in self.instance.player_manager.online:
				if ko_start_timer:
					await ko_start_timer.display(player)
			await asyncio.sleep(1)

		await ko_start_timer.destroy()
		await self.instance.gbx('RestartMap')


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
		for signal, target in self.context.signals.listeners:
			if target == self.set_ko_settings:
				signal.unregister(target)

		await self.instance.mode_manager.set_next_script('Rounds.Script.txt')

		await self.instance.gbx('RestartMap')
		while await self.instance.mode_manager.get_current_full_script() != 'Rounds.Script.txt':
			await asyncio.sleep(1)
		await self.set_ko_modesettings()

		self.context.signals.listen(mp_signals.flow.round_end, self.knockout_players)
		self.context.signals.listen(mp_signals.flow.round_start, self.display_nr_of_kos)


	async def set_ko_modesettings(self):
		settings = await self.instance.mode_manager.get_settings()

		settings['S_PointsLimit'] = -1
		settings['S_RoundsPerMap'] = -1
		settings['S_WarmUpNb'] = 1
		settings['S_WarmUpDuration'] = settings['wu_duration']
		settings['S_PointsRepartition'] = ','.join(str(x) for x in range(len(self.ko_qualified), 0, -1))
		settings['S_FinishTimeout'] = self.timeout

		await self.instance.mode_manager.update_settings(settings)


	async def get_qualified(self, count, time):
		for signal, target in self.context.signals.listeners:
			if target == self.get_qualified:
				signal.unregister(target)

		ta_results = (await self.instance.gbx('Trackmania.GetScores'))['players']
		self.ta_finishers = [record['login'] for record in ta_results if record['bestracetime'] != -1]

		if not self.ta_finishers:
			await self.reset_server()
			return

		self.ko_qualified = [p for (i,p) in enumerate(self.ta_finishers) if i < len(self.ta_finishers)/2]
		for p in self.instance.player_manager.online_logins:
			if p in self.ta_finishers:
				if p in self.ko_qualified:
					await self.nc_chat('Well done, you qualified for the KO phase!', p)
					await self.instance.gbx('ForceSpectator', p, 2)
				else:
					await self.nc_chat('Unlucky, you did not qualify for the KO phase!', p)
					await self.force_spec_or_kick(p)
			else:
				await self.force_spec_or_kick(p)


	async def knockout_players(self, count, time):
		nr_kos = await self.get_nr_kos(len(self.ko_qualified))
		round_scores = (await self.instance.gbx('Trackmania.GetScores'))['players']
		round_scores = [(record['login'], record['prevracetime']) for record in round_scores if record['login'] in self.ko_qualified]

		round_scores.sort(key=itemgetter(1))
		round_scores = [p for p in round_scores if p[1] != -1]
		if len(round_scores) == 0:
			return

		round_logins = [p[0] for p in round_scores]

		if len(self.ko_qualified) <= 2:
			await self.nc_chat(f'Player {(await Player.get_by_login(round_scores[0][0])).nickname}{self.chat_reset} wins this RPG NightCup, well played!')
			await self.reset_server()
			return

		dnfs = [p for p in self.ko_qualified if p not in round_logins]
		kos = round_logins[len(self.ko_qualified)-nr_kos:]
		qualified = round_logins[:len(self.ko_qualified)-nr_kos]
		for i,p in enumerate(kos, start=1):
			await self.nc_chat(f'You have been eliminated from this KO: position {len(qualified) + i}/{len(self.ko_qualified)}', p)
			await self.force_spec_or_kick(p)
		for p in dnfs:
			await self.nc_chat(f'You have been eliminated from this KO: position DNF/{len(self.ko_qualified)}', p)
			await self.force_spec_or_kick(p)
		for i,p in enumerate(qualified, start=1):
			await self.nc_chat(f'You are still in! position {i}/{len(self.ko_qualified)}', p)
			await self.instance.gbx('ForceSpectator', p, 2)

		kos.extend(dnfs)
		kos = [(await Player.get_by_login(login)).nickname for login in kos]
		kos_string = f'{self.chat_reset}, '.join(kos)
		await self.nc_chat(f'Players knocked out: {kos_string}')

		self.ko_qualified = [p for p in self.ko_qualified if p in qualified]


	async def force_spec_or_kick(self, p):
		if self.instance.player_manager.count_spectators < self.instance.player_manager.max_spectators:
			await self.instance.gbx('ForceSpectator', p, 1)
		else:
			await self.instance.gbx('Kick', p)


	async def display_nr_of_kos(self, count, time):
		await self.nc_chat(f'{len(self.ko_qualified)} players left, number of KOs: {await self.get_nr_kos(len(self.ko_qualified))}')


	async def get_nr_kos(self, nr_players):
		return int((nr_players + 4) / 10) + 1


	async def nc_chat(self, message, player=None):
		if player:
			await self.instance.chat(f'{self.chat_prefix}{message}', player)
		else:
			await self.instance.chat(f'{self.chat_prefix}{message}')


	async def nc_settings(self, player, *args, **kwargs):
		settings_view = SettingsListView(self, player)
		await settings_view.display(player=player)


	async def get_long_settings(self):
		return self.settings_long


	async def update_settings(self, new_settings):
		self.settings = new_settings
		for key in new_settings:
			for setting_long in self.settings_long:
				if setting_long['name'] == key:
					setting_long['value'] = new_settings[key]
