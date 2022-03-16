import datetime
from peewee import *
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.db import Model


class Rank(Model):
	player = ForeignKeyField(Player, index=True)
	"""
	Player that has driven this time.
	"""

	average = IntegerField()
	"""
	Average map ranking.
	"""

	calculated_at = DateTimeField(
		default=datetime.datetime.now,
	)
	"""
	When is the time driven?
	"""

	class Meta:
		db_table = 'stats_ranks'
