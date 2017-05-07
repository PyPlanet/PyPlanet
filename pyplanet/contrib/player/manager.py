import asyncio
import datetime

from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.conf import settings
from pyplanet.contrib import CoreContrib
from pyplanet.contrib.player.exceptions import PlayerNotFound


class PlayerManager(CoreContrib):
	"""
	Player Manager.
	
	.. todo::
	
		Write introduction.
		
	.. warning::
	
		Don't initiate this class yourself.
	"""
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		# Online contains all currently online players.
		self._online = set()

	async def on_start(self):
		"""
		Handle startup, just before the apps will start. We will throw connects for the players so we know that the 
		current playing players are also initiated correctly!
		"""
		player_list = await self._instance.gbx.execute('GetPlayerList', -1, 0)
		await asyncio.gather(*[self.handle_connect(player['Login']) for player in player_list])

	async def handle_connect(self, login):
		"""
		Handle a connection of a player, this call is being called inside of the Glue of the callbacks.
		
		:param login: Login, received from dedicated.
		:return: Database Player instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.Player
		"""
		# Ignore if it's the server itself.
		if self._instance.game.server_is_dedicated and self._instance.game.server_player_login == login:
			return

		info = await self._instance.gbx.execute('GetDetailedPlayerInfo', login)
		ip, _, port = info['IPAddress'].rpartition(':')
		is_owner = login in settings.OWNERS[self._instance.process_name]
		try:
			player = await Player.get_by_login(login)
			player.last_ip = ip
			player.last_seen = datetime.datetime.now()
			player.nickname = info['NickName']
			if is_owner:
				player.level = Player.LEVEL_MASTER
			await player.save()
		except DoesNotExist:
			# Get details of player from dedicated.
			player = await Player.create(
				login=login,
				nickname=info['NickName'],
				last_ip=ip,
				last_seen=datetime.datetime.now(),
				level=Player.LEVEL_MASTER if is_owner else Player.LEVEL_PLAYER,
			)

		player.flow.player_id = info['PlayerId']
		player.flow.team_id = info['TeamId']

		self._online.add(player)

		return player

	async def handle_disconnect(self, login):
		"""
		Handle a disconnection of a player, this call is being called inside of the Glue of the callbacks.
		
		:param login: Login, received from dedicated.
		:return: Database Player instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.Player 
		"""
		player = await Player.get(login=login)
		if player in self._online:
			self._online.remove(player)
		player.last_seen = datetime.datetime.now()
		await player.save()

		return player

	async def get_player(self, login=None, pk=None, lock=True):
		"""
		Get player by login or primary key.
		
		:param login: Login.
		:param pk: Primary Key identifier.
		:param lock: Lock for a sec when receiving.
		:return: Player or exception if not found
		:rtype: pyplanet.apps.core.maniaplanet.models.Player
		"""
		try:
			if login:
				return await Player.get_by_login(login)
			elif pk:
				return await Player.get(pk=pk)
			else:
				raise PlayerNotFound('Player not found.')
		except DoesNotExist:
			if lock:
				await asyncio.sleep(1)
				return await self.get_player(login=login, pk=pk, lock=False)
			else:
				raise PlayerNotFound('Player not found.')

	async def get_player_by_id(self, identifier):
		for player in self._online:
			if player.flow.player_id == identifier:
				return player
		return None

	@property
	def online(self):
		"""
		Online player list.
		"""
		return self._online
