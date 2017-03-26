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

	map_style = CharField(max_length=255, null=True, default=None)
	"""
	Style of the map.
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

	CACHE = dict()

	def __str__(self):
		return '\'{}\' by {} ({})'.format(self.name, self.author_login, self.uid)

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		self.CACHE[self.uid] = self

	@classmethod
	def get_by_uid(cls, uid):
		"""
		Get map by UID.
		:param uid: UId.
		:return: Map instance
		:rtype: pyplanet.apps.core.maniaplanet.models.map.Map
		"""
		if uid in cls.CACHE:
			return cls.CACHE[uid]
		return cls.get(uid=uid)

	@cached_property
	def author(self):
		from .player import Player

		if self.author_login:
			Player.get(login=self.author_login)
		return None

	@classmethod
	def get_or_create_from_info(cls, uid, file, name, author_login, **kwargs):
		"""
		This method will be called from the core, getting or creating a map instance from the information we got from
		the dedicated server.
		:param uid: Map UID
		:param file: Filename
		:param name: Name of map
		:param author_login: Author login
		:param kwargs: Other key arguments, matching the model columns!
		:return: Map instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.map.Map
		"""
		needs_save = False
		try:
			map = cls.get_by_uid(uid)
			if map.file != file or map.name != name:
				map.file = file
				map.name = name
				needs_save = True
		except DoesNotExist:
			map = Map(uid=uid, file=file, name=name, author_login=author_login)
			needs_save = True

		# Update from the kwargs.
		for k, v in kwargs.items():
			if v is not None and hasattr(map, k) and getattr(map, k) != v:
				setattr(map, k, v)
				needs_save = True

		if needs_save:
			map.save()

		return map
