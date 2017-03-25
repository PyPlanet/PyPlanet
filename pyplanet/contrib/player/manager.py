import datetime

from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.player.exceptions import PlayerNotFound


class PlayerManager:
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		# Cache will only be used internally. Always ordered by key => model instance.
		self._cache = dict()

		# Online contains all currently online players.
		self._online = set()

	async def handle_connect(self, login):
		"""
		Handle a connection of a player, this call is being called inside of the Glue of the callbacks.
		:param login: Login, received from dedicated.
		:return: Database Player instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.Player
		"""
		info = await self._instance.gbx.execute('GetDetailedPlayerInfo', login)
		ip, _, port = info['IPAddress'].rpartition(':')
		try:
			player = Player.get(login=login)
			player.last_ip = ip
			player.last_seen = datetime.datetime.now()
			player.save()
		except DoesNotExist:
			# Get details of player from dedicated.
			player = Player.create(
				login=login,
				nickname=info['NickName'],
				last_ip=ip,
				last_seen=datetime.datetime.now()
			)

		self._online.add(player)

	async def handle_disconnect(self, login):
		"""
		Handle a disconnection of a player, this call is being called inside of the Glue of the callbacks.
		:param login: Login, received from dedicated.
		:return: Database Player instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.Player 
		"""
		player = Player.get(login=login)
		player.last_seen = datetime.datetime.now()
		player.save()
		self._online.remove(player)

	async def get_player(self, login=None, pk=None):
		"""
		Get player by login or primary key.
		:param login: Login.
		:param id: Primary Key identifier.
		:return: Player or exception if not found
		:rtype: pyplanet.apps.core.maniaplanet.models.Player
		"""
		try:
			if login and login in self._cache:
				return self._cache[login]

			if pk:
				player = Player.get(pk=pk)
			elif login:
				player = Player.get(login=login)
			else:
				raise PlayerNotFound('Player not found.')

			self._cache[login] = player
			return player
		except DoesNotExist:
			raise PlayerNotFound('Player not found.')
