import asyncio
import datetime
import logging

from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.conf import settings
from pyplanet.contrib import CoreContrib
from pyplanet.contrib.player.exceptions import PlayerNotFound
from pyplanet.contrib.setting.core_settings import performance_mode
from pyplanet.core.signals import pyplanet_performance_mode_begin, pyplanet_performance_mode_end

logger = logging.getLogger(__name__)


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
		self._performance_mode = False
		# self.lock = asyncio.Lock()

		# Online contains all currently online players.
		self._online = set()

	@property
	def performance_mode(self):
		return self._performance_mode

	@performance_mode.setter
	def performance_mode(self, new_value):
		if self._performance_mode != new_value:
			if new_value:
				asyncio.ensure_future(
					pyplanet_performance_mode_begin.send_robust(source=dict(
						old_value=self._performance_mode, new_value=new_value
					))
				)
			else:
				asyncio.ensure_future(
					pyplanet_performance_mode_end.send_robust(source=dict(
						old_value=self._performance_mode, new_value=new_value
					))
				)
		self._performance_mode = new_value

	async def on_start(self):
		"""
		Handle startup, just before the apps will start. We will throw connects for the players so we know that the 
		current playing players are also initiated correctly!
		"""
		player_list = await self._instance.gbx('GetPlayerList', -1, 0)
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

		try:
			info = await self._instance.gbx('GetDetailedPlayerInfo', login)
		except:
			# Most likely too late, did disconnect directly after connecting..
			# See #126
			return
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
		self.performance_mode = len(self._online) >= await performance_mode.get_value()

		return player

	async def handle_disconnect(self, login):
		"""
		Handle a disconnection of a player, this call is being called inside of the Glue of the callbacks.
		
		:param login: Login, received from dedicated.
		:return: Database Player instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.Player 
		"""
		try:
			player = await Player.get_by_login(login=login)
		except:
			return

		if player in self._online:
			self._online.remove(player)
		try:
			del Player.CACHE[login]
		except:
			pass
		player.last_seen = datetime.datetime.now()
		await player.save()

		self.performance_mode = len(self._online) >= await performance_mode.get_value()

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
				await asyncio.sleep(4)
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
		return self._online.copy()
