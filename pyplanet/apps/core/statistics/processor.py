"""
This file contains several queries and logic to fetch statistics that can be displayed on the statistics views.
Please note that this file is only meant for the statistics app, and can change at any time!
"""
import asyncio

from datetime import datetime
from peewee import JOIN

from pyplanet.apps.contrib.local_records import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Map, Player
from pyplanet.apps.core.statistics.models import Score, fn


class StatisticsProcessor:
	"""
	Statistics Processor.
	Please don't use this outside of the statistics app as the API will change without any info before.
	"""
	def __init__(self, app):
		"""
		Init the processor

		:param app: App instance.
		:type app: pyplanet.apps.core.statistics.Statistics
		"""
		self.app = app

		self.topsums_cache = None
		self.topsums_cache_time = None

	async def get_dashboard_data(self, player):
		"""
		Get player fact numbers, such as the number of finishes. Number of top-3 records, etc.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: dictionary with results.
		"""
		# Combine several calls.
		finishes, top_3, records = await asyncio.gather(
			self.get_num_finishes(player),
			self.get_num_top_3(player),
			self.get_num_records(player),
		)

		return dict(
			numbers=dict(
				finishes=finishes,
				top_3=top_3,
				records=records,
			),
		)

	async def get_num_finishes(self, player):
		"""
		Get the number of finishes.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: count or False when not possible to fetch.
		:rtype: int
		"""
		if self.app.instance.game.game == 'tm':
			return await Score.objects.count(
				Score.select(Score).where(Score.player == player)
			)
		return False

	async def get_num_records(self, player):
		"""
		Get the number of local records.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: count or False when not possible to fetch.
		:rtype: int
		"""
		if self.app.instance.game.game == 'tm' and 'local_records' in self.app.instance.apps.apps:
			return await LocalRecord.objects.count(
				LocalRecord.select(LocalRecord).where(LocalRecord.player == player)
			)
		return False

	async def get_num_top_3(self, player):
		"""
		Get the number of top-3 records of one player.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: count or False when not possible to fetch.
		:rtype: int
		"""
		# Get the players number of top-3 records (tm only + when local records is active).
		if self.app.instance.game.game == 'tm' and 'local_records' in self.app.instance.apps.apps:
			top = 0
			records = await LocalRecord.objects.execute(
				LocalRecord.select(LocalRecord).where(LocalRecord.player == player)
			)
			for record in records:
				top_3 = await LocalRecord.objects.execute(
					LocalRecord.select(LocalRecord).where(LocalRecord.map_id == record.map_id).limit(3)
				)
				if record in top_3:
					top += 1
			return top
		return False

	async def get_topsums(self):
		"""
		Get the topsums of the server.

		:return: List of top 100 players on the server with the statistics.
		"""
		if 'local_records' not in self.app.instance.apps.apps:
			return None

		now = datetime.now()
		diff = now - self.topsums_cache_time if self.topsums_cache_time else False
		if not self.topsums_cache or not diff or diff.total_seconds() > 60:
			self.topsums_cache = None
			self.topsums_cache_time = None
		elif self.topsums_cache:
			return self.topsums_cache

		maps = self.app.instance.map_manager.maps
		players = dict()

		for map_instance in maps:
			res = await LocalRecord.objects.execute(
				LocalRecord.select(LocalRecord, Player)
					.join(Player)
					.where(LocalRecord.map_id == map_instance.id)
					.order_by(LocalRecord.score)
					.limit(3)
			)
			for rank, entry in enumerate(res):
				if entry.player not in players:
					players[entry.player] = [0, 0, 0]
				players[entry.player][rank] += 1

		topsums = list(players.items())
		topsums.sort(key=lambda item: item[1][0] + item[1][1] + item[1][2], reverse=True)

		self.topsums_cache = topsums[:100]
		self.topsums_cache_time = datetime.now()
		return self.topsums_cache

	async def get_top_active_players(self):
		"""
		Get the top active players of the server.

		:return: List of top 100 players on the server ordered by the total playtimes.
		"""
		return await Player.objects.execute(
			Player.select(Player)
				.order_by(-Player.total_playtime)
				.limit(100)
		)

	async def get_top_donating_players(self):
		"""
		Get the top donating players of the server.

		:return: List of top 100 players on the server ordered by the total donations.
		"""
		return await Player.objects.execute(
			Player.select(Player)
				.order_by(-Player.total_donations)
				.limit(100)
		)
