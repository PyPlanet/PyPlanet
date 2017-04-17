"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel
from pyplanet.apps.core.maniaplanet.models import Map, Player

class LocalRecord(TimedModel):
	map = ForeignKeyField(Map)
	"""
	Map on which the local record is driven.
	"""

	player = ForeignKeyField(Player)
	"""
	Player who drove the local record.
	"""

	score = IntegerField(
		null=False
	)
	"""
	Time/score of the local record.
	"""

	checkpoints = TextField(
		null=False
	)
	"""
	List of checkpoints of the local record.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def save(self, *args, **kwargs):
		await super().save(*args, **kwargs)

	'''@classmethod
	async def get_by_map(cls, map):
		"""
		Get records by map.
		:param map: Map.
		:return: List of LocalRecord instances
		:rtype: pyplanet.apps.core.maniaplanet.models.player.LocalRecord[]
		"""
		return await LocalRecord.objects.filter(map_id=map.get_id)'''
