"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel
from pyplanet.apps.core.maniaplanet.models import Map, Player


class LocalRecord(TimedModel):
	map = ForeignKeyField(Map, index=True)
	"""
	Map on which the local record is driven.
	"""

	player = ForeignKeyField(Player, index=True)
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
		null=False, default=''
	)
	"""
	List of checkpoints of the local record.
	"""

	class Meta:
		indexes = (
			(('player', 'map'), True),
		)
