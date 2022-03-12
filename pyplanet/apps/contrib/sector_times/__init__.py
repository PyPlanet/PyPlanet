"""
Sector Times.
"""
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.sector_times.views import SectorTimesWidget, CheckpointDiffWidget, GearIndicatorView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting
from pyplanet.core.signals import pyplanet_start_after


class SectorTimes(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.sector_widget = SectorTimesWidget(self)
		self.cp_widget = CheckpointDiffWidget(self)
		self.gear_view = GearIndicatorView(self)

		self.setting_enable_gear_indicator = Setting(
			'gear_indicator', 'Enable Gear Indicator', Setting.CAT_FEATURES, type=bool, default=True,
			description='Enable the Gear Indicator View in Stadium based titles',
			change_target=self.reload_settings
		)
		self.gear_view_possible = False

	async def on_start(self):
		await self.context.setting.register(
			self.setting_enable_gear_indicator
		)

		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)

		self.context.signals.listen(pyplanet_start_after, self.on_after_start)

		self.gear_view_possible = \
			self.instance.map_manager.current_map.environment == 'Stadium' and self.instance.game.game == 'tm'

		# Set the MP CP diff widget position.
		if self.instance.game.game in ['tm', 'sm']:
			self.instance.ui_manager.properties.set_attribute('checkpoint_time', 'pos', '0. 8. -10.')

	def is_mode_supported(self, mode):
		return mode != 'Trackmania/TM_RoyalTimeAttack_Online'

	async def on_after_start(self, *args, **kwargs):
		await asyncio.sleep(1)
		asyncio.ensure_future(asyncio.gather(*[
			self.player_connect(p) for p in self.instance.player_manager.online
		]))

	async def player_connect(self, player, **kwargs):
		await self.sector_widget.display(player)
		await self.cp_widget.display(player)
		if self.gear_view_possible and await self.setting_enable_gear_indicator.get_value():
			await self.gear_view.display(player.login)

	async def map_start(self, *args, **kwargs):
		await asyncio.sleep(2)
		await self.sector_widget.display()
		await self.cp_widget.display()

	async def podium_start(self, *args, **kwargs):
		await self.sector_widget.hide()
		await self.cp_widget.hide()

	async def reload_settings(self, *args, **kwargs):
		if await self.setting_enable_gear_indicator.get_value() and self.gear_view_possible:
			await self.gear_view.display()
		else:
			await self.gear_view.hide()
