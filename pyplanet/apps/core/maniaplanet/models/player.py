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

	total_playtime = IntegerField(default=0, null=False)
	"""
	The total playtime of the player
	"""

	total_donations = IntegerField(default=0, null=False)
	"""
	The total donations given by the player.
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
		self.__attributes = PlayerAttributes()
		super().__init__(*args, **kwargs)

	@property
	def flow(self):
		"""
		Flow object of the player.

		:return: flow object
		:rtype: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
		"""
		return self.__flow

	@property
	def attributes(self):
		return self.__attributes

	async def save(self, *args, **kwargs):
		res = await super().save(*args, **kwargs)
		if self.login not in self.CACHE or (self.login in self.CACHE and id(self) != id(self.CACHE[self.login])):
			if self.login in self.CACHE and id(self) != id(self.CACHE[self.login]):
				self.__flow = self.CACHE[self.login].flow
				self.__attributes = self.CACHE[self.login].attributes
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
		self.force_spectator = None
		self.is_referee = None
		self.is_podium_ready = None
		self.is_using_stereoscopy = None
		self.is_managed_by_other_server = None
		self.is_server = None
		self.has_player_slot = None
		self.is_broadcasting = None
		self.has_joined_game = None
		self.zone = None
		self.joined_at = None

		self.royal_server_start_time = 0
		self.royal_total_time = 0
		self.royal_section_time = 0
		self.royal_times = list()
		self.royal_block_ids = list()

		self.other = dict()

	def start_run(self):
		self.in_run = True

	def handle_waypoint_royal(self, race_time, server_time, block_id):
		"""
		Returns true if handled.
		"""
		if block_id in self.royal_block_ids:
			return False
		self.royal_block_ids.append(block_id)

		time = server_time - self.royal_server_start_time

		self.royal_total_time += time
		self.royal_section_time += time
		self.royal_times.append(self.royal_section_time)

		return True

	def reset_royal(self, server_time):
		self.royal_server_start_time = server_time
		self.royal_total_time = 0
		self.royal_section_time = 0
		self.royal_block_ids = list()
		self.royal_times = list()

	def handle_give_up_royal(self, server_time):
		penalty = 1500
		time = server_time - self.royal_server_start_time + penalty
		self.royal_total_time += time
		self.royal_section_time += time

	def handle_start_line_royal(self, server_time):
		self.royal_server_start_time = server_time

	def handle_match_begin_royal(self):
		self.royal_times = list()
		self.royal_block_ids = list()
		self.royal_server_start_time = 0
		self.royal_section_time = 0
		self.royal_total_time = 0

	def reset_run(self):
		if self.in_run:
			self.in_run = False

	def update_state(self, **data):
		self.is_spectator = data.pop('is_spectator')
		self.is_player = not self.is_spectator
		self.spectator_target = data.pop('target')
		self.team_id = data.pop('team_id')

		for key, value in data.items():
			setattr(self, key, value)

	def reset_state(self):
		self.is_player = None
		self.is_spectator = None
		self.is_pure_spectator = None
		self.is_temp_spectator = None
		self.force_spectator = None
		self.is_referee = None
		self.is_podium_ready = None
		self.is_using_stereoscopy = None
		self.is_managed_by_other_server = None
		self.is_server = None
		self.has_player_slot = None
		self.is_broadcasting = None
		self.has_joined_game = None


class PlayerAttributes:
	"""
	Hold custom attributes by keys used in several apps.
	"""
	def __init__(self):
		self.__attributes = dict()

	def set(self, key, value):
		"""
		Set value of a defined key.

		:param key: Key string
		:param value: Value of the attribute
		:type key: str
		"""
		self.__attributes[key] = value

	def get(self, key, default=None):
		"""
		Get value of the key (or the default value).

		:param key: Key string
		:param default: Default value, defaults to None
		:return: The value of the attribute.
		"""
		if key in self.__attributes:
			return self.__attributes[key]
		return default

	def all(self):
		"""
		Get all attributes as dictionary. Please don't change attributes this way as the backend of the attributes may change
		over time!

		:return: Dict of attributes.
		:rtype: dict
		"""
		return self.__attributes
