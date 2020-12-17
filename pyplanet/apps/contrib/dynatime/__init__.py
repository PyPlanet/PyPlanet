import logging

from pyplanet.apps.config import AppConfig

from pyplanet.contrib.setting import Setting
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.map.exceptions import ModeIncompatible
from pyplanet.utils.times import format_time
from pyplanet.utils.style import STRIP_ALL, style_strip

logger = logging.getLogger(__name__)


class DynatimeApp(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next']
	mode_dependencies = ['TimeAttack']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setting_dynatime_active = Setting(
			'dynatime_active', 'Dynatime Active', Setting.CAT_BEHAVIOUR, type=bool,
			description='Activate Dynamic Round timer based on map bronze time',
			default=True
		)

		self.setting_dynatime_announce = Setting(
			'dynatime_accounce', 'Dynatime Accounce', Setting.CAT_BEHAVIOUR, type=bool,
			description='Announce the current timelimit at the start of each round',
			default=True
		)

		self.setting_dynatime_multiplier = Setting(
			'dynatime_multiplier', 'Dynatime Multiplier', Setting.CAT_BEHAVIOUR, type=int,
			description='Multiply map bronze time by this amount to get round timer',
			default=5
		)

	async def on_init(self):
		await super().on_init()

	async def on_start(self):
		await super().on_start()

		await self.context.setting.register(
			self.setting_dynatime_active,
			self.setting_dynatime_announce,
			self.setting_dynatime_multiplier,
		)

		self.context.signals.listen(mp_signals.map.map_begin, self.on_map_begin)


	async def on_stop(self):
		await super().on_stop()

	async def on_destroy(self):
		await super().on_destroy()

	async def on_map_begin(self, map, **kwargs):
		is_active = await self.setting_dynatime_active.get_value()
		if not is_active:
			return

		multiplier = await self.setting_dynatime_multiplier.get_value(refresh=True)
		mode_settings = await self.instance.mode_manager.get_settings()

		if 'S_TimeLimit' not in mode_settings:
			raise ModeIncompatible('Current mode doesn\'t support Dynatime. Not TimeAttack?')

		timelimit = int(multiplier * map.time_bronze / 1000)
		timelimit_ms = timelimit * 1000

		mode_settings['S_TimeLimit'] = timelimit

		bm_time = format_time(time=map.time_bronze, hide_milliseconds=True)
		new_time = format_time(time=timelimit_ms, hide_milliseconds=True)
		mname = style_strip(map.name, STRIP_ALL)
		chat_message = "$FF0$oDynatime$z$s set new timelimit for map $fff%s$z$ff0 to $fff⏳ %s$ff0, based on the bronze-medal of $fff🏆 %s$z" % ( mname, new_time, bm_time )

		await self.instance.mode_manager.update_settings(mode_settings)

		announce = await self.setting_dynatime_announce.get_value()
		if announce:
			await self.instance.chat(chat_message)
