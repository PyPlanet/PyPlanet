"""
This file contains several queries and logic to fetch statistics that can be displayed on the statistics views.
Please note that this file is only meant for the statistics app, and can change at any time!
"""
from pprint import pprint

import asyncio

from pyplanet.apps.contrib.local_records import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Map
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
