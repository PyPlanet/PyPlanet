import asyncio
import collections

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.nightcup.views import TimerView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.command import Command

class NightCup(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	TIME_UNTIL_TA_PHASE = 5 * 60
	TIME_UNTIL_KO_PHASE = 5 * 60
	TIME_AFTER_KO_PHASE = 5 * 60
	TIME_UNTIL_NEXT_WALL = 3
	TIME_TA = 45 * 60
	TIMEOUT = 90


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.ta_finishers = []
		self.ko_qualified = []

		self.chat_reset = '$z$fff$s'
		self.chat_prefix = f'$i$080NightCup - {self.chat_reset}'

		self.nc_active = False

		self.backup_script_name = None
		self.backup_settings = None

		self.open_views = []


	async def on_init(self):
		await super().on_init()


	async def on_start(self):
		# Registering permissions
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
				perms='brawl_match:nc_control'
			),
			Command(
				'stop',
				namespace='nc',
				target=self.stop_nc,
				perms='brawl_match:nc_control'
			)
		)


	async def start_nc(self, admin, *args, **kwargs):
		if self.match_tasks:
			await self.nc_chat(f'A nightcup is currently in progress!', admin)
		else:
			await self.nc_chat(f'Nightcup is starting now!', admin)
			self.nc_active = True
			await self.backup_mode_settings()
			await asyncio.sleep(self.TIME_UNTIL_NEXT_WALL)
			await self.set_ta_settings()
			self.context.signals.listen(mp_signals.map.map_begin, self.set_ko_settings)


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
			if target in [self.set_ko_settings]:
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


	async def set_ko_settings(self):
		await self.instance.mode_manager.set_next_script('Rounds.Script.txt')

		await self.instance.gbx('RestartMap')
		while await self.instance.mode_manager.get_current_full_script() != 'Rounds.Script.txt':
			await asyncio.sleep(1)
		await self.set_ko_modesettings()


	async def set_ko_modesettings(self):
		settings = await self.instance.mode_manager.get_settings()

		settings['S_PointsLimit'] = -1
		settings['S_RoundsPerMap'] = -1
		settings['S_WarmUpNb'] = 0
		settings['S_FinishTimeout'] = self.TIMEOUT
		settings['S_ChatTime'] = self.TIME_AFTER_KO_PHASE

		await self.instance.mode_manager.update_settings(settings)


	async def nc_chat(self, message, player=None):
		if player:
			await self.instance.chat(f'{self.chat_prefix}{message}', player)
		else:
			await self.instance.chat(f'{self.chat_prefix}{message}')
