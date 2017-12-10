import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.core.trackmania import callbacks as tm_signals

from .view import BestCpTimesWidget
from .view import CpTimesListView


class BestCpTimes(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']
	# mode_dependencies = ['TimeAttack']

	best_cp_times = []

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.number_of_checkpoints = None
		self.best_cp_times = []  # List of PlayerCP Objects
		self.widget = None

	async def on_start(self):
		self.context.signals.listen(tm_signals.waypoint, self.player_cp)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.map.map_begin, self.map_begin)
		self.context.signals.listen(mp_signals.map.map_start__end, self.map_end)
		self.best_cp_times.clear()
		self.widget = BestCpTimesWidget(self)
		asyncio.ensure_future(self.widget.display())

	# When a player passes a CP
	async def player_cp(self, player, raw, *args, **kwargs):
		cpnm = int(raw['checkpointinlap'])
		laptime = int(raw['laptime'])
		pcp = PlayerCP(player, cpnm + 1, laptime)
		if not self.best_cp_times:
			self.best_cp_times.append(pcp)
		else:
			added = False
			for idx, current_cp in enumerate(self.best_cp_times):
				if pcp.cp < current_cp.cp:
					self.best_cp_times.insert(idx, pcp)
					added = True
					break
				elif pcp.cp == current_cp.cp:
					if laptime < current_cp.time:
						self.best_cp_times[idx] = pcp
					added = True
					break
			if not added:
				self.best_cp_times.append(pcp)
		await self.widget.display()

	# When the map starts
	async def map_begin(self, *args, **kwargs):
		self.best_cp_times.clear()
		await self.widget.display()

	# When the map ends. This is needed to not keep the old CP data when the map is restarted.
	async def map_end(self, *args, **kwargs):
		self.best_cp_times.clear()
		await self.widget.display()

	# When a player connects
	async def player_connect(self, player, **kwargs):
		await self.widget.display(player)


# PlayerCP Event mapping a player to a cp and a time
class PlayerCP:
	def __init__(self, player, cp=0, time=0):
		self.player = player
		self.cp = cp
		self.time = time
