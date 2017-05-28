"""
Dynamic points limit for Shootmania Royal.
"""
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting


class DynamicPoints(AppConfig):
	game_dependencies = ['shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.enabled = False

		self.current_limit = None
		self.next_limit = None

		self.setting_enable_dynamic_points = Setting(
			'dynamic_points', 'Enable dynamic points limit', Setting.CAT_FEATURES, type=bool,
			description='Enable the dynamic points limit for Shootmania Royal.',
			default=True, change_target=self.enable_changed
		)
		self.setting_min_points = Setting(
			'min_points', 'Minimum number of points', Setting.CAT_GENERAL, type=int,
			description='The points limit will never go bellow this number of points.',
			default=10, change_target=self.on_changes
		)
		self.setting_max_points = Setting(
			'min_points', 'Maximum number of points', Setting.CAT_GENERAL, type=int,
			description='The points limit will never go above this number of points. Leave at 0 to disable.',
			default=0, change_target=self.on_changes
		)
		self.setting_points_per_player = Setting(
			'min_points', 'Points per player', Setting.CAT_GENERAL, type=int,
			description='The points every player should increase the total points limit of the map.',
			default=10, change_target=self.on_changes
		)
		self.setting_change_during_map = Setting(
			'change_during_map', 'Change during map gameplay', Setting.CAT_FEATURES, type=bool,
			description='Enable this to change points during a map gameplay.',
			default=True, change_target=self.on_changes
		)
		self.setting_announce_points_change = Setting(
			'announce_change', 'Announce points change at map start/end', Setting.CAT_FEATURES, type=bool,
			description='The points every player should increase the total points limit of the map.',
			default=True, change_target=self.on_changes
		)

	def enable_changed(self, old, new):
		self.enabled = new

	def is_mode_supported(self, mode):
		return 'royal' in mode.lower()

	async def on_start(self):
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.on_changes)
		self.instance.signal_manager.listen(mp_signals.player.player_disconnect, self.on_changes)
		self.instance.signal_manager.listen(mp_signals.player.player_info_changed, self.on_changes)
		self.instance.signal_manager.listen(mp_signals.map.map_start, self.map_start)

		await self.context.setting.register(
			self.setting_enable_dynamic_points, self.setting_min_points, self.setting_max_points,
			self.setting_points_per_player, self.setting_announce_points_change, self.setting_change_during_map
		)
		self.enabled = await self.setting_enable_dynamic_points.get_value()

		if self.enabled:
			await self.on_changes(enable_announce=True)

	async def on_changes(self, *args, **kwargs):
		if not self.enabled:
			return
		point_per_player = await self.setting_points_per_player.get_value()
		if point_per_player <= 0:
			return

		player_count = self.instance.player_manager.count_players
		total_points = player_count * point_per_player

		if await self.setting_change_during_map.get_value():
			self.current_limit = total_points
			await self.set_limit(total_points, disable_announce='enable_announce' not in kwargs)
			self.next_limit = None
		else:
			self.next_limit = total_points

	async def set_limit(self, new_limit, disable_announce=False):
		min_limit, max_limit, announce = await asyncio.gather(
			self.setting_min_points.get_value(),
			self.setting_max_points.get_value(),
			self.setting_announce_points_change.get_value(),
		)

		if min_limit > 0 and new_limit < min_limit:
			new_limit = min_limit
		if max_limit > 0 and new_limit > max_limit:
			new_limit = max_limit
		if new_limit <= 0 or not new_limit:
			return

		await self.instance.mode_manager.update_settings({
			'S_MapPointsLimit': int(new_limit)
		})
		if announce and not disable_announce:
			await self.instance.chat(
				'$ff0The points limit has been changed to $fff{}$z$s$ff0.'.format(new_limit)
			)

	async def map_start(self, *args, **kwargs):
		if self.next_limit and not await self.setting_change_during_map.get_value():
			self.current_limit = self.next_limit
			await self.set_limit(self.next_limit, disable_announce=kwargs.get('restarted', False))
			self.next_limit = None
