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

	You can access this class in your app with:

	.. code-block:: python

		self.instance.player_manager

	With the manager you can get several useful information about the players on the server. See all the properties and methods
	below for more information.

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

		# Counters.
		self._counter_lock = asyncio.Lock()
		self._total_count = 0
		self._players_count = 0
		self._spectators_count = 0

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

		# Update counter and state.
		async with self._counter_lock:
			player.flow.player_id = info['PlayerId']
			player.flow.team_id = info['TeamId']
			player.flow.is_spectator = bool(info['IsSpectator'])
			player.flow.is_player = not bool(info['IsSpectator'])

			self._total_count += 1
			if player.flow.is_spectator:
				self._spectators_count += 1
			else:
				self._players_count += 1

		self._online.add(player)
		self.performance_mode = len(self._online) >= await performance_mode.get_value()

		return player

	async def handle_info_change(self, player, is_spectator, is_temp_spectator, is_pure_spectator, target, team_id, **kwargs):
		if not player:
			return

		async with self._counter_lock:
			if player.flow.is_spectator is True and not is_spectator:
				self._spectators_count -= 1
				self._players_count += 1

				await self._instance.signal_manager.get_signal('maniaplanet:player_enter_player_slot').send_robust(dict(
					player=player,
				), raw=True)
			elif player.flow.is_player is True and is_spectator:
				self._spectators_count += 1
				self._players_count -= 1

				await self._instance.signal_manager.get_signal('maniaplanet:player_enter_spectator_slot').send_robust(dict(
					player=player,
				), raw=True)

			# This is in case of desync happens. Not nice to fix, but currently one of the only options.
			if self._players_count < 0:
				self._players_count = 0
			if self._spectators_count < 0:
				self._spectators_count = 0
			if self._total_count < 0:
				self._total_count = 0

		player.flow.is_spectator = is_spectator
		player.flow.is_temp_spectator = is_temp_spectator
		player.flow.is_pure_spectator = is_pure_spectator
		player.flow.is_player = not is_spectator
		player.flow.spectator_target = target
		player.flow.team_id = team_id

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

		# Update counters.
		async with self._counter_lock:
			self._total_count -= 1
			if player.flow.is_player:
				self._players_count -= 1
			else:
				self._spectators_count -= 1

		if player in self._online:
			self._online.remove(player)
		try:
			del Player.CACHE[login]
		except:
			pass
		player.last_seen = datetime.datetime.now()
		await player.save()

		# Clear player/spec state.
		player.flow.is_player = None
		player.flow.is_spectator = None
		player.flow.is_pure_spectator = None
		player.flow.is_temp_spectator = None

		# Update performance mode status.
		self.performance_mode = self._total_count >= await performance_mode.get_value()

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

	@property
	def count_all(self):
		"""
		Get all player counts (players + spectators).
		"""
		return self._total_count

	@property
	def count_players(self):
		"""
		Get number of playing players.
		"""
		return self._players_count

	@property
	def count_spectators(self):
		"""
		Get number of spectating players.
		"""
		return self._spectators_count

	@property
	def max_players(self):
		"""
		Get maximum number of players.
		"""
		return self._instance.game.server_max_players

	@property
	def max_spectators(self):
		"""
		Get maximum number of spectators.
		"""
		return self._instance.game.server_max_specs
