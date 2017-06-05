"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel
from pyplanet.utils.functional import empty


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
		self.__flow = PlayerFlow()
		super().__init__(*args, **kwargs)

	@property
	def flow(self):
		return self.__flow

	async def save(self, *args, **kwargs):
		res = await super().save(*args, **kwargs)
		if self.login not in self.CACHE or (self.login in self.CACHE and id(self) != id(self.CACHE[self.login])):
			if self.login in self.CACHE and id(self) != id(self.CACHE[self.login]):
				self.__flow = self.CACHE[self.login].flow
			self.CACHE[self.login] = self
		return res

	@classmethod
	async def get_by_login(cls, login, default=empty):
		"""
		Get player by login.

		:param login: Login.
		:param default: Optional default if not exist.
		:return: Player instance
		:rtype: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		if login in cls.CACHE:
			return cls.CACHE[login]
		try:
			cls.CACHE[login] = player = await cls.get(login=login)
		except DoesNotExist:
			if default is not empty:
				return default
			raise
		return player

	def get_level_string(self):
		for level_nr, level_name in self.LEVEL_CHOICES:
			if self.level == level_nr:
				return level_name
		return None


class PlayerFlow:
	def __init__(self):
		self.in_run = False
		self.player_id = None
		self.team_id = None
		self.is_player = None
		self.is_spectator = None
		self.is_temp_spectator = None
		self.is_pure_spectator = None
		self.spectator_target = None
		self.other = dict()

	def start_run(self):
		self.in_run = True

	def reset_run(self):
		if self.in_run:
			self.in_run = False
