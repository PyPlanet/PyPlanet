"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from cached_property import cached_property
from peewee import *
from pyplanet.core.db import TimedModel


class Map(TimedModel):
	uid = CharField(
		max_length=50,
		null=False,
		index=True,
		unique=True,
	)
	"""
	The uid of the map will be unique in our database as it's unique over all maps (unique identifier).
	"""

	name = CharField(max_length=150)
	"""
	The name of the map, can contain unparsed styles.
	"""

	file = CharField(max_length=255)
	"""
	Filename and path from root of the maps directory of the dedicated server.
	"""

	author_login = CharField(max_length=100)
	"""
	Author login of the map.
	"""

	author_nickname = CharField(max_length=150, null=True, default=None)
	"""
	Author nickname as of saving the map. (Parsed from the Gbx file).
	"""

	environment = CharField(max_length=30, null=True, default=None)
	"""
	Environment of the map. Sample: Canyon
	"""

	title = CharField(max_length=255, null=True, default=None)
	"""
	The title of the map. Samples: TMCanyon, TMCanyon@nadeo, etc.
	"""

	map_type = CharField(max_length=255, null=True, default=None)
	"""
	Type of map in slashes. Like: Trackmania\Race
	"""

	num_laps = IntegerField(null=True, default=None)
	"""
	Number of laps if multilap map, else None.
	"""

	num_checkpoints = IntegerField(null=True, default=None)
	"""
	Number of checkpoints. Could be not know (yet).
	"""

	price = IntegerField(null=True, default=None)
	"""
	Price of graphical impact. None if not yet investigated.
	"""

	time_author = IntegerField(null=True, default=None)
	time_bronze = IntegerField(null=True, default=None)
	time_silver = IntegerField(null=True, default=None)
	time_gold = IntegerField(null=True, default=None)
	"""
	Time of author and all medals.
	"""

	@cached_property
	def author(self):
		from .player import Player

		if self.author_login:
			Player.get(login=self.author_login)
		return None
