"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel


class Player(TimedModel):
	LEVEL_PLAYER = 0
	LEVEL_OPERATOR = 1
	LEVEL_ADMIN = 2
	LEVEL_MASTER = 3
	LEVEL_CHOICES = (
		(LEVEL_PLAYER, 'Player'),
		(LEVEL_OPERATOR, 'Operator'),
		(LEVEL_ADMIN, 'Admin'),
		(LEVEL_MASTER, 'MasterAdmin'),
	)

	login = CharField(
		max_length=100,
		null=False,
		index=True,
		unique=True
	)
	"""
	The login of the player will be the unique index we use in the player table.
	"""

	nickname = CharField(max_length=150)
	"""
	The nickname of the player including maniaplanet styles.
	"""

	last_ip = CharField(max_length=46, null=True, default=None)
	"""
	The last used IP-address for the player.
	"""

	last_seen = DateTimeField(null=True, default=None)
	"""
	When is the player last seen on the server.
	"""

	level = IntegerField(choices=LEVEL_CHOICES, default=LEVEL_PLAYER)
	"""
	The level of the player. See the LEVEL_CHOICES tuple. Use methods like get_level_string on player object to retrieve
	the name of the level.
	"""

	CACHE = dict()

	def __str__(self):
		return self.login

	def __init__(self, *args, **kwargs):
		self.__data = dict()
		super().__init__(*args, **kwargs)

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		self.CACHE[self.login] = self

	@classmethod
	def get_by_login(cls, login):
		"""
		Get player by login.
		:param login: Login.
		:return: Player instance
		:rtype: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		if login in cls.CACHE:
			return cls.CACHE[login]
		return cls.get(login=login)

	def data(self):
		return self.__data

	def get_level_string(self):
		for level_nr, level_name in self.LEVEL_CHOICES:
			if self.level == level_nr:
				return level_name
		return None
