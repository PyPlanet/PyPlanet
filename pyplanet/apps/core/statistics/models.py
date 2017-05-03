import datetime
from peewee import *

from pyplanet.apps.core.maniaplanet.models import Map, Player
from pyplanet.core.db import Model


class Score(Model):
	map = ForeignKeyField(Map, index=True)
	"""
	The map the player did play.
	"""

	player = ForeignKeyField(Player, index=True)
	"""
	Player that has driven this time.
	"""

	score = IntegerField()
	"""
	Score (points or time).
	"""

	checkpoints = TextField()
	"""
	The checkpoint times, separated by commas.
	"""

	created_at = DateTimeField(
		default=datetime.datetime.now,
	)
	"""
	When is the time driven?
	"""

	class Meta:
		db_table = 'stats_scores'
