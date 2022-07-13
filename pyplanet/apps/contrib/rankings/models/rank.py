import datetime
from peewee import *
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.db import Model


class Rank(Model):
	player = ForeignKeyField(Player, index=True)
	"""
	Player that has the rank.
	"""

	average = IntegerField()
	"""
	Average map ranking.
	"""

	calculated_at = DateTimeField(
		default=datetime.datetime.now,
	)
	"""
	When was the rank calculated?
	"""

	class Meta:
		db_table = 'rankings_rank'
