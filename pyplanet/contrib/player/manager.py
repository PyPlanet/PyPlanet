import asyncio
import datetime

from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.player.exceptions import PlayerNotFound
from pyplanet.core.events import receiver
from pyplanet.core import signals


class PlayerManager:
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		# Online contains all currently online players.
		self._online = set()

		# Initiate the self instances on receivers.
		self.handle_startup()

	@receiver(signals.pyplanet_start_apps_before)
	async def handle_startup(self, **kwargs):
		"""
		Handle startup, just before the apps will start. We will throw connects for the players so we know that the 
		current playing players are also initiated correctly!
		:param kwargs: Ignored parameters.
		"""
		player_list = await self._instance.gbx.execute('GetPlayerList', -1, 1)
		await asyncio.gather(*[self.handle_connect(player['Login']) for player in player_list])

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
			player = await Player.get(login=login)
			player.last_ip = ip
			player.last_seen = datetime.datetime.now()
			await player.save()
		except DoesNotExist:
			# Get details of player from dedicated.
			player = await Player.create(
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
		:param pk: Primary Key identifier.
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
			raise PlayerNotFound('Player not found.')
