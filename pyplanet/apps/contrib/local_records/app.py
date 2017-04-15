from pyplanet.apps.config import AppConfig
from pyplanet.core.events import receiver

from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.utils import times


class LocalRecordsConfig(AppConfig):
	name = 'pyplanet.apps.contrib.local_records'
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	async def on_ready(self):
		self.player_finish()

	@receiver(tm_signals.finish)
	async def player_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		message = '$z$s> Player {}$z$s drove a time of {}'.format(player.nickname, times.format_time(race_time))
		await self.instance.gbx.execute('ChatSendServerMessage', message)
