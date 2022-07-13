from peewee import *
from pyplanet.core.db import Model


class RankedMap(Model):
	id = IntegerField()
	"""
	ID of the map on which the player has the rank.
	"""

	name = CharField(max_length=150)
	"""
	Name of the map on which the player has the rank.
	"""

	uid = CharField(max_length=50)
	"""
	UID of the map on which the player has the rank.
	"""

	author_login = CharField(max_length=100)
	"""
	Author login of the map on which the player has the rank.
	"""

	player_rank = IntegerField()
	"""
	Rank the player has on the map.
	"""
