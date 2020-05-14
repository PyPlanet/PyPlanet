import asyncio
import math
from operator import itemgetter

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.nightcup.views import TimerView, SettingsListView
from pyplanet.apps.contrib.nightcup.standings import StandingsLogicManager
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
				'value': 6
			},
			{
				'default': '2700',
				'type': int,
				'name': 'nc_ta_length',
				'description': 'Length of TA phase',
				'value': 40
			},
			{
				'default': '600',
				'type': int,
				'name': 'nc_time_until_ko',
				'description': 'Time between TA phase and KO phase',
				'value': 6
			},
			{
				'default': '60',
				'type': int,
				'name': 'nc_wu_duration',
				'description': 'Length of warmups for players to load the map',
				'value': 6
			}
		]

		self.settings = {setting['name']: setting['value'] for setting in self.settings_long}
		self.chat_reset = '$z$fff$s'
		self.chat_prefix = f'$fffRPG $036NIGHTCUP $fff- {self.chat_reset}'

		self.nc_active = False
		self.ta_active = False
		self.ko_active = False

		self.backup_script_name = None
		self.backup_settings = None
		self.backup_dedi_ui_params = {}

		self.open_views = []

		self.standings_logic_manager = StandingsLogicManager(self)


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
			),
			Command(
				'addqualified',
				namespace='nc',
				aliases=['aq'],
				target=self.add_qualified,
				perms='nightcup:nc_control',
				admin=True
			).add_param(
				'player',
				nargs='*',
				type=str,
				required=True
			),
			Command(
				'removequalified',
				namespace='nc',
				aliases=['rq'],
				target=self.remove_qualified,
				perms='nightcup:nc_control',
				admin=True
			).add_param(
				'player',
				nargs='*',
				type=str,
				required=True
			)
		)
		await self.standings_logic_manager.start()


	async def start_nc(self, player, *args, **kwargs):
		if self.nc_active:
			await self.nc_chat(f'A nightcup is currently in progress!', player)
		else:
			await self.nc_chat(f'Nightcup is starting now!')
			await self.set_ui_elements()


			self.nc_active = True
			await self.backup_mode_settings()
			await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)

			await self.wait_for_ta_start()


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


	async def wait_for_ta_start(self):
		ta_start_timer = TimerView(self)
		self.open_views.append(ta_start_timer)
		ta_start_timer.title = f"TA phase starts in {await self.format_time(self.settings['nc_time_until_ta'])}"
		for player in self.instance.player_manager.online:
			await ta_start_timer.display(player)

		secs = 0
		while self.settings['nc_time_until_ta'] - secs > 0 and ta_start_timer:
			ta_start_timer.title = f"TA phase starts in {await self.format_time(self.settings['nc_time_until_ta'] - secs)}"
			for player in self.instance.player_manager.online:
				if not ta_start_timer is None:
					await ta_start_timer.display(player)
			await asyncio.sleep(1)
			secs += 1

		await ta_start_timer.destroy()
		await self.instance.gbx('RestartMap')

		await self.set_ta_settings()
		self.ta_active = True
		await self.standings_logic_manager.set_standings_widget_title('TA Phase')
		await self.standings_logic_manager.set_liverankings_listeners()
		self.context.signals.listen(mp_signals.flow.round_end, self.get_qualified)
		self.context.signals.listen(mp_signals.flow.round_end, self.wait_for_ko_start)


	async def wait_for_ko_start(self, count, time):
		self.ta_active = False
		await self.standings_logic_manager.set_standings_widget_title('Current CPs')
		await self.standings_logic_manager.set_currentcps_listeners()
		settings = await self.instance.mode_manager.get_settings()
		settings['S_TimeLimit'] = -1
		settings['S_WarmUpDuration'] = 0
		settings['S_WarmUpNb'] = -1
		await self.instance.mode_manager.update_settings(settings)

		await self.unregister_signals([self.wait_for_ko_start])

		await self.instance.gbx('RestartMap')

		self.context.signals.listen(mp_signals.map.map_begin, self.set_ko_settings)
		ko_start_timer = TimerView(self)
		self.open_views.append(ko_start_timer)
		ko_start_timer.title = f"KO phase starts in {await self.format_time(self.settings['nc_time_until_ko'])}"
		for player in self.instance.player_manager.online:
			await ko_start_timer.display(player)

		secs = 0
		while self.settings['nc_time_until_ko'] - secs > 0 and ko_start_timer:
			ko_start_timer.title = f"KO phase starts in {await self.format_time(self.settings['nc_time_until_ko'] - secs)}"
			for player in self.instance.player_manager.online:
				if ko_start_timer:
					await ko_start_timer.display(player)
			await asyncio.sleep(1)
			secs += 1

		await ko_start_timer.destroy()
		await self.instance.map_manager.set_next_map(self.instance.map_manager.current_map)
		self.ko_active = True
		await self.standings_logic_manager.set_standings_widget_title('KO phase')
		await self.instance.gbx('NextMap')


	async def format_time(self, seconds):
		return f'{seconds // 60}:{seconds % 60:02d}'


	async def stop_nc(self, player, *args, **kwargs):
		if not self.nc_active:
			await self.nc_chat(f'No nightcup is currently in progress!', player)
			return
		await self.nc_chat(f'Admin {player.nickname}{self.chat_reset} stopped nightcup!')
		await self.reset_server()


	async def reset_server(self):
		self.ta_active = False
		self.ko_active = False
		await self.standings_logic_manager.set_standings_widget_title('Current CPs')

		for view in self.open_views:
			await view.destroy()
		self.open_views.clear()

		await self.unregister_signals(
			[self.set_ko_settings, self.get_qualified, self.knockout_players, self.display_nr_of_kos]
		)

		self.ta_finishers.clear()
		self.ko_qualified.clear()

		await self.reset_backup()
		await self.reset_ui_elements()


	async def reset_backup(self):
		if not (self.backup_script_name and self.backup_settings):
			return

		await asyncio.sleep(5)
		await self.instance.mode_manager.set_next_script(self.backup_script_name)
		await self.instance.mode_manager.update_next_settings(self.backup_settings)
		await self.instance.gbx('RestartMap')

		self.nc_active = False


	async def set_ko_settings(self, map):
		await self.unregister_signals([self.set_ko_settings])

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
		settings['S_WarmUpDuration'] = self.settings['nc_wu_duration']
		settings['S_PointsRepartition'] = ','.join(str(x) for x in range(len(self.ko_qualified), 0, -1))
		settings['S_FinishTimeout'] = self.timeout

		await self.instance.mode_manager.update_settings(settings)


	async def get_qualified(self, count, time):
		await self.unregister_signals([self.get_qualified])

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
		round_scores = (await self.instance.gbx('Trackmania.GetScores'))['players']
		nr_kos = await self.get_nr_kos(len(self.ko_qualified))
		round_scores = [(record['login'], record['prevracetime']) for record in round_scores if record['login'] in self.ko_qualified]

		round_scores.sort(key=itemgetter(1))
		round_scores = [p for p in round_scores if p[1] != -1]
		if len(round_scores) == 0:
			return

		round_logins = [p[0] for p in round_scores]

		if len(self.ko_qualified) <= 2 or len(round_scores) == 1:
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
			await self.instance.gbx('ForceSpectator', p, 3)
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


	async def add_qualified(self, player, data, **kwargs):
		if not self.nc_active:
			await self.nc_chat('$i$f00No nightcup is currently active', player)
			return
		players_to_add = data.player
		for player_to_add in players_to_add:
			if not player_to_add in self.instance.player_manager.online_logins:
				await self.nc_chat('$i$f00Player is currently not on the server', player)
				continue
			self.ko_qualified.append(player_to_add)
			await self.nc_chat(f'Player {(await Player.get_by_login(player_to_add)).nickname} '
							   f'has been added to the qualified list')


	async def remove_qualified(self, player, data, **kwargs):
		if not self.nc_active:
			await self.nc_chat('$i$f00No nightcup is currently active', player)
			return
		players_to_remove = data.player
		for player_to_remove in players_to_remove:
			if not player_to_remove in self.ko_qualified:
				await self.nc_chat('$i$f00Player is currently not in the qualified list', player)
				continue
			self.ko_qualified.remove(player_to_remove)
			await self.nc_chat(f'Player {(await Player.get_by_login(player_to_remove)).nickname} '
							   f'has been removed from the qualified list')


	async def set_ui_elements(self):
		await self.move_dedi_ui()

	# for app in self.instance.ui_manager.app_managers.values():
	# 	live_rankings = app.manialinks.get('pyplanet__widgets_liverankings')
	# 	current_cps = app.manialinks.get('pyplanet__widgets_currentcps')
	# 	if live_rankings:
	# 		await live_rankings.hide()
	# 	if current_cps:
	# 		await current_cps.hide()


	async def move_dedi_ui(self):
		for app in self.instance.ui_manager.app_managers.values():
			dedi_view = app.manialinks.get('pyplanet__widgets_dedimaniarecords')
			if dedi_view:
				self.backup_dedi_ui_params = {
					'top_entries': dedi_view.top_entries,
					'record_amount': dedi_view.record_amount,
					'widget_x': dedi_view.widget_x,
					'widget_y': dedi_view.widget_y
				}
				dedi_view.top_entries = 1
				dedi_view.record_amount = 5
				dedi_view.widget_x = 125
				dedi_view.widget_y = 0

				await dedi_view.display()

	async def reset_ui_elements(self):
		await self.reset_dedi_ui()

	# for app in self.instance.ui_manager.app_managers.values():
	# 	live_rankings = app.manialinks.get('pyplanet__widgets_liverankings')
	# 	current_cps = app.manialinks.get('pyplanet__widgets_currentcps')
	# 	if live_rankings:
	# 		await live_rankings.display()
	# 	if current_cps:
	# 		await current_cps.display()

	async def reset_dedi_ui(self):
		for app in self.instance.ui_manager.app_managers.values():
			dedi_view = app.manialinks.get('pyplanet__widgets_dedimaniarecords')
			if dedi_view:
				dedi_view.top_entries = self.backup_dedi_ui_params['top_entries']
				dedi_view.record_amount = self.backup_dedi_ui_params['record_amount']
				dedi_view.widget_x = self.backup_dedi_ui_params['widget_x']
				dedi_view.widget_y = self.backup_dedi_ui_params['widget_y']

				await dedi_view.display()

	async def unregister_signals(self, targets):
		for signal, target in self.context.signals.listeners:
			if target in targets:
				signal.unregister(target)

	async def get_nr_qualified(self):
		if self.ta_active:
			print(self.ta_finishers)
			return math.ceil(len(self.ta_finishers) / 2)
		if self.ko_active:
			return len(self.ko_qualified) - await self.get_nr_kos(len(self.ko_qualified))
		return -1

	async def spec_player(self, player, target_login):
		await self.instance.gbx.multicall(
			self.instance.gbx('ForceSpectator', player.login, 3),
			self.instance.gbx('ForceSpectatorTarget', player.login, target_login, -1)
		)
