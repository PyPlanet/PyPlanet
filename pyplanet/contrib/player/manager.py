import asyncio
import datetime
import logging

from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.conf import settings
from pyplanet.contrib import CoreContrib
from pyplanet.contrib.player.exceptions import PlayerNotFound
from pyplanet.contrib.setting.core_settings import performance_mode
from pyplanet.core.exceptions import ImproperlyConfigured
from pyplanet.core.signals import pyplanet_performance_mode_begin, pyplanet_performance_mode_end
from pyplanet.core.storage.exceptions import StorageException
from pyplanet.utils.zone import parse_path

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
		self._online_logins = set()

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

		# Load and activate blacklist.
		try:
			await self.load_blacklist()
		except:
			pass  # Ignore any exception thrown

		self._instance.signals.listen('maniaplanet:loading_map_end', self.map_loaded)

	async def map_loaded(self, *args, **kwargs):
		"""
		Reindex the current number of players and spectators.

		:param args:
		:param kwargs:
		:return:
		"""
		# Update player and spectator counters.
		player_list = await self._instance.gbx('GetPlayerList', -1, 0)

		total = 0
		specs = 0
		players = 0

		for player in player_list:
			if self._instance.game.server_is_dedicated and self._instance.game.server_player_login == player['Login']:
				continue

			try:
				info = await self._instance.gbx('GetDetailedPlayerInfo', player['Login'])
			except:
				# Player has left during this time.
				continue

			total += 1
			if info['IsSpectator']:
				specs += 1
			else:
				players += 1

		async with self._counter_lock:
			self._total_count = total
			self._spectators_count = specs
			self._players_count = players

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

		# Set the join time.
		player.flow.joined_at = datetime.datetime.now()

		# Update counter and state.
		async with self._counter_lock:
			player.flow.player_id = info['PlayerId']
			player.flow.team_id = info['TeamId']
			player.flow.is_spectator = bool(info['IsSpectator'])
			player.flow.is_player = not bool(info['IsSpectator'])
			player.flow.zone = parse_path(info['Path'])

			self._total_count += 1
			if player.flow.is_spectator:
				self._spectators_count += 1
			else:
				self._players_count += 1

		self._online.add(player)
		self._online_logins.add(login)
		self.performance_mode = len(self._online) >= await performance_mode.get_value()

		return player

	async def handle_info_change(self, player, is_spectator, is_temp_spectator, is_pure_spectator, target, team_id, **kwargs):
		if not player:
			return

		if player not in self._online:
			return

		async with self._counter_lock:
			if player.flow.is_spectator is True and not is_spectator:
				self._spectators_count -= 1
				self._players_count += 1

				await self._instance.signals.get_signal('maniaplanet:player_enter_player_slot').send_robust(dict(
					player=player,
				), raw=True)
			elif player.flow.is_player is True and is_spectator:
				self._spectators_count += 1
				self._players_count -= 1

				await self._instance.signals.get_signal('maniaplanet:player_enter_spectator_slot').send_robust(dict(
					player=player,
				), raw=True)

			# This is in case of desync happens. Not nice to fix, but currently one of the only options.
			if self._players_count < 0:
				self._players_count = 0
			if self._spectators_count < 0:
				self._spectators_count = 0
			if self._total_count < 0:
				self._total_count = 0

		# Update flow state.
		payload = kwargs.copy()
		payload.update(dict(
			is_spectator=is_spectator, is_temp_spectator=is_temp_spectator, is_pure_spectator=is_pure_spectator,
			target=target, team_id=team_id
		))
		player.flow.update_state(**payload)

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
		if login in self._online_logins:
			self._online_logins.remove(login)

		# Calculate the number of seconds on the server and update the total time on server.
		if player.flow.joined_at:
			time_on_server = datetime.datetime.now() - player.flow.joined_at
			player.total_playtime += int(time_on_server.total_seconds())

		try:
			del Player.CACHE[login]
		except:
			pass
		player.last_seen = datetime.datetime.now()
		await player.save()

		# Clear player/spec state.
		player.flow.reset_state()

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
		"""
		Get player object by ID.

		:param identifier: Identifier.
		:return: Player object or None
		"""
		for player in self._online:
			if player.flow.player_id == identifier:
				return player
		return None

	async def save_blacklist(self, filename=None):
		"""
		Save the current blacklisted players to file given or fetch from config.

		:param filename: Give the filename of the blacklist, Leave empty to use the current loaded and configured one.
		:type filename: str
		:raise: pyplanet.core.exceptions.ImproperlyConfigured
		:raise: pyplanet.core.storage.exceptions.StorageException
		"""
		setting = settings.BLACKLIST_FILE
		if isinstance(setting, dict) and self._instance.process_name in setting:
			setting = setting[self._instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not filename and not setting:
			raise ImproperlyConfigured(
				'The setting \'BLACKLIST_FILE\' is not configured for this server! We can\'t save the Blacklist!'
			)
		if not filename:
			filename = setting.format(server_login=self._instance.game.server_player_login)
		
		try:
			await self._instance.gbx('SaveBlackList', filename)
		except Exception as e:
			logging.exception(e)
			raise StorageException('Can\'t save blacklist file to \'{}\'!'.format(filename)) from e

	async def save_guestlist(self, filename=None):
		"""
		Save the current guestlisted players to file given or fetch from config.

		:param filename: Give the filename of the guestlist, Leave empty to use the current loaded and configured one.
		:type filename: str
		:raise: pyplanet.core.exceptions.ImproperlyConfigured
		:raise: pyplanet.core.storage.exceptions.StorageException
		"""
		setting = settings.GUESTLIST_FILE
		if isinstance(setting, dict) and self._instance.process_name in setting:
			setting = setting[self._instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not filename and not setting:
			raise ImproperlyConfigured(
				'The setting \'GUESTLIST_FILE\' is not configured for this server! We can\'t save the Guestlist!'
			)
		if not filename:
			filename = setting.format(server_login=self._instance.game.server_player_login)

		try:
			await self._instance.gbx('SaveGuestList', filename)
		except Exception as e:
			logging.exception(e)
			raise StorageException('Can\'t save guestlist file to \'{}\'!'.format(filename)) from e


	async def load_guestlist(self, filename=None):
		"""
		Load guestlist file.

		:param filename: File to load or will get from settings.
		:raise: pyplanet.core.exceptions.ImproperlyConfigured
		:raise: pyplanet.core.storage.exceptions.StorageException
		:return: Boolean if loaded.
		"""
		setting = settings.GUESTLIST_FILE
		if isinstance(setting, dict) and self._instance.process_name in setting:
			setting = setting[self._instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not filename and not setting:
			raise ImproperlyConfigured(
				'The setting \'GUESTLIST_FILE\' is not configured for this server! We can\'t load the Guestlist!'
			)
		if not filename:
			filename = setting.format(server_login=self._instance.game.server_player_login)

		try:
			self._instance.gbx('LoadGuestList', filename)
		except Exception as e:
			logging.exception(e)
			raise StorageException('Can\'t load guestlist according the dedicated server, tried loading from \'{}\'!'.format(
				filename
			)) from e

	async def load_blacklist(self, filename=None):
		"""
		Load blacklist file.

		:param filename: File to load or will get from settings.
		:raise: pyplanet.core.exceptions.ImproperlyConfigured
		:raise: pyplanet.core.storage.exceptions.StorageException
		:return: Boolean if loaded.
		"""
		setting = settings.BLACKLIST_FILE
		if isinstance(setting, dict) and self._instance.process_name in setting:
			setting = setting[self._instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not filename and not setting:
			raise ImproperlyConfigured(
				'The setting \'BLACKLIST_FILE\' is not configured for this server! We can\'t load the Blacklist!'
			)
		if not filename:
			filename = setting.format(server_login=self._instance.game.server_player_login)

		try:
			self._instance.gbx('LoadBlackList', filename)
		except Exception as e:
			logging.exception(e)
			raise StorageException('Can\'t load blacklist according the dedicated server, tried loading from \'{}\'!'.format(
				filename
			)) from e

	@property
	def online(self):
		"""
		Online player list.
		"""
		return self._online.copy()

	@property
	def online_logins(self):
		"""
		Online player logins list.
		"""
		return self._online_logins.copy()

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
