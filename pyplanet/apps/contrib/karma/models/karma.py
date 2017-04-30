"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel
from pyplanet.apps.core.maniaplanet.models import Map, Player


class Karma(TimedModel):
	map = ForeignKeyField(Map, index=True)
	"""
	Map on which the player voted.
	"""

	player = ForeignKeyField(Player, index=True)
	"""
	The player who voted.
	"""

	score = IntegerField(
		null=False
	)
	"""
	Karma vote (-1 or 1)
	"""
