import asyncio
import os
import logging

from xmlrpc.client import Fault
from peewee import DoesNotExist

from pyplanet.utils.log import handle_exception
from pyplanet.apps.core.maniaplanet.models import Map
from pyplanet.conf import settings
from pyplanet.contrib import CoreContrib
from pyplanet.contrib.map.exceptions import MapNotFound, MapException
from pyplanet.core.exceptions import ImproperlyConfigured


class MapManager(CoreContrib):
	"""
	Map Manager. Manages the current map pool and the current and next map.

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
		self.lock = asyncio.Lock()

		# The matchsettings contains the name of the current loaded matchsettings file.
		self._matchsettings = None

		# The maps contain a list of map instances in the order that are in the current loaded list.
		self._maps = set()

		# The current map will always be in this variable. The next map will always be here. It will be updated. once
		# it's updated it should be send to the dedicated to queue the next map.
		self._previous_map = None
		self._current_map = None
		self._next_map = None

	async def on_start(self):
		self._instance.signal_manager.listen('maniaplanet:playlist_modified', lambda: '')

		# Fully update list + database.
		await self.update_list(full_update=True)

		# Get current and next map.
		self._current_map, self._next_map = await asyncio.gather(
			self.handle_map_change(await self._instance.gbx('GetCurrentMapInfo')),
			self.handle_map_change(await self._instance.gbx('GetNextMapInfo')),
		)
		self._previous_map = None

	async def handle_map_change(self, info):
		"""
		This will be called from the glue that creates the signal 'maniaplanet:map_begin' or 'map_end'.

		:param info: Mapinfo in dict.
		:return: Map instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.map.Map
		"""
		map_info = await Map.get_or_create_from_info(
			uid=info['UId'], name=info['Name'], author_login=info['Author'], file=info['FileName'],
			environment=info['Environnement'], map_type=info['MapType'], map_style=info['MapStyle'],
			num_laps=info['NbLaps'], num_checkpoints=info['NbCheckpoints'], time_author=info['AuthorTime'],
			time_bronze=info['BronzeTime'], time_silver=info['SilverTime'], time_gold=info['GoldTime'],
			price=info['CopperPrice']
		)
		self._previous_map = self._current_map
		self._current_map = map_info
		return map_info

	async def handle_playlist_change(self, source, **kwargs):
		return await self.update_list()

	async def update_list(self, full_update=False):
		raw_list = await self._instance.gbx('GetMapList', -1, 0)
		updated = list()

		if full_update:
			# We will initiate the maps in the database (or update).
			coroutines = [Map.get_or_create_from_info(
				details['UId'], details['FileName'], details['Name'], details['Author'],
				environment=details['Environnement'], time_gold=details['GoldTime'],
				price=details['CopperPrice'], map_type=details['MapType'], map_style=details['MapStyle']
			) for details in raw_list]

			maps = await asyncio.gather(*coroutines)
			async with self.lock:
				self._maps = set(maps)
		else:
			# Only update/insert the changed bits, (not checking for removed maps!!).
			async with self.lock:
				for details in raw_list:
					if not any(m.uid == details['UId'] for m in self._maps):
						# Map not yet in self._maps. Add it.
						map_instance = await Map.get_or_create_from_info(
							details['UId'], details['FileName'], details['Name'], details['Author'],
							environment=details['Environnement'], time_gold=details['GoldTime'],
							price=details['CopperPrice'], map_type=details['MapType'], map_style=details['MapStyle']
						)
						self._maps.add(map_instance)
						updated.append(map_instance)
		return updated

	async def get_map(self, uid=None):
		"""
		Get map instance by uid.

		:param uid: By uid (pk).
		:return: Player or exception if not found
		"""
		try:
			return await Map.get_by_uid(uid)
		except DoesNotExist:
			raise MapNotFound('Map not found.')

	async def get_map_by_index(self, index):
		"""
		Get map instance by index id (primary key).

		:param index: Primary key index.
		:return: Map instance or raise exception.
		"""
		try:
			return await Map.get(id=index)
		except DoesNotExist:
			raise MapNotFound('Map not found.')

	@property
	def next_map(self):
		"""
		The next scheduled map.

		:rtype: pyplanet.apps.core.maniaplanet.models.Map
		"""
		return self._next_map

	async def set_next_map(self, map):
		"""
		Set the next map. This will prepare the manager to set the next map and will communicate the next map to the
		dedicated server.

		The Map parameter can be a map instance or the UID of the map.

		:param map: Map instance or UID string.
		:type map: pyplanet.apps.core.maniaplanet.models.Map, str
		"""
		if isinstance(map, str):
			map = await self.get_map(map)
		if not isinstance(map, Map):
			raise Exception('When setting the map, you should give an Map instance!')
		if map.file:
			await self._instance.gbx('ChooseNextMap', map.file)
		else:
			await self._instance.gbx('SetNextMapIdent', map.uid)
		self._next_map = map

	@property
	def current_map(self):
		"""
		The current map, database model instance.

		:rtype: pyplanet.apps.core.maniaplanet.models.Map
		"""
		return self._current_map

	@property
	def previous_map(self):
		"""
		The previously played map, or None if not known!

		:rtype: pyplanet.apps.core.maniaplanet.models.Map
		"""
		return self._previous_map

	@property
	def maps(self):
		"""
		Get the maps that are currently loaded on the server. The list should contain model instances of the currently
		loaded matchsettings. This list should be up-to-date.

		:rtype: list
		"""
		return self._maps

	async def set_current_map(self, map):
		"""
		Set the current map and jump to it.

		:param map: Map instance or uid.
		"""
		if isinstance(map, str):
			map = await self.get_map(map)
		if not isinstance(map, Map):
			raise Exception('When setting the map, you should give an Map instance!')

		await self._instance.gbx('JumpToMapIdent', map.uid)
		self._next_map = map

	def playlist_has_map(self, uid):
		"""
		Check if our current playlist has a map with the UID given.

		:param uid: UID String
		:return: Boolean, True if it's in our current playlist (match settings in our session).
		"""
		for map_instance in self.maps:
			if map_instance.uid == uid:
				return True
		return False

	async def add_map(self, filename, insert=True, save_matchsettings=True):
		"""
		Add or insert map to current online playlist.

		:param filename: Load from filename relative to the 'Maps' directory on the dedicated host server.
		:param insert: Insert after the current map, this will make it play directly after the current map. True by default.
		:param save_matchsettings: Save match settings as well.
		:type filename: str
		:type insert: bool
		:type save_matchsettings: bool
		:raise: pyplanet.contrib.map.exceptions.MapIncompatible
		:raise: pyplanet.contrib.map.exceptions.MapException
		"""
		gbx_method = 'InsertMap' if insert else 'AddMap'

		try:
			result = await self._instance.gbx(gbx_method, filename)
		except Fault as e:
			if 'unknown' in e.faultString:
				raise MapNotFound('Map is not found on the server.')
			elif 'already' in e.faultString:
				raise MapException('Map already added to server.')
			raise MapException(e.faultString)

		# Try to save match settings.
		try:
			if save_matchsettings:
				await self.save_matchsettings()
		except Exception as e:
			handle_exception(e, __name__, 'add_map', extra_data={'EXTRAHOOK': 'Map Insert bug, see #306'})

		return result

	async def upload_map(self, fh, filename, insert=True, overwrite=False):
		"""
		Upload and add/insert the map to the current online playlist.

		:param fh: File handler, bytesio object or any readable context.
		:param filename: The filename when saving on the server. Must include the map.gbx! Relative to 'Maps' folder.
		:param insert: Insert after the current map, this will make it play directly after the current map. True by default.
		:param overwrite: Overwrite current file if exists? Default False.
		:type filename: str
		:type insert: bool
		:type overwrite: bool
		:raise: pyplanet.contrib.map.exceptions.MapIncompatible
		:raise: pyplanet.contrib.map.exceptions.MapException
		:raise: pyplanet.core.storage.exceptions.StorageException
		"""
		exists = await self._instance.storage.driver.exists(filename)
		if exists and not overwrite:
			raise MapException('Map with filename already located on server!')
		if not exists:
			await self._instance.storage.driver.touch('{}{}'.format(self._instance.storage.MAP_FOLDER, filename))

		async with self._instance.storage.open_map(filename, 'wb+') as fw:
			await fw.write(fh.read(-1))

		return await self.add_map(filename, insert=insert)

	async def remove_map(self, map, delete_file=False):
		"""
		Remove and optionally delete file from server and playlist.

		:param map: Map instance or filename in string.
		:param delete_file: Boolean to decide if we are going to remove the file from the server too. Defaults to False.
		:type delete_file: bool
		:raise: pyplanet.contrib.map.exceptions.MapException
		:raise: pyplanet.core.storage.exceptions.StorageException
		"""
		if isinstance(map, Map):
			map = map.file
		if not isinstance(map, str):
			raise ValueError('Map must be instance or string uid!')

		try:
			success = await self._instance.gbx('RemoveMap', map)
			if success:
				the_map = None
				for m in self._maps:
					if m.file == map:
						the_map = m
						break
				if the_map:
					self._maps.remove(the_map)
		except Fault as e:
			if 'unknown' in e.faultString:
				raise MapNotFound('Dedicated can\'t find map. Already removed?')
			raise MapException('Error when removing map from playlist: {}'.format(e.faultString))

		# Try to save match settings.
		try:
			await self.save_matchsettings()
		except:
			pass

		# Delete the actual file.
		if delete_file:
			try:
				await self._instance.storage.remove_map(map)
			except:
				raise MapException('Can\'t delete map file after removing from playlist.')

	async def save_matchsettings(self, filename=None):
		"""
		Save the current playlist and configuration to the matchsettings file.

		:param filename: Give the filename of the matchsettings, Leave empty to use the current loaded and configured one.
		:type filename: str
		:raise: pyplanet.contrib.map.exceptions.MapException
		:raise: pyplanet.core.storage.exceptions.StorageException
		"""
		setting = settings.MAP_MATCHSETTINGS
		if isinstance(setting, dict) and self._instance.process_name in setting:
			setting = setting[self._instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not filename and not setting:
			raise ImproperlyConfigured(
				'The setting \'MAP_MATCHSETTINGS\' is not configured for this server! We can\'t save the Match Settings!'
			)
		if not filename:
			filename = 'MatchSettings/{}'.format(
				setting.format(server_login=self._instance.game.server_player_login)
			)

		try:
			await self._instance.gbx('SaveMatchSettings', filename)
		except Exception as e:
			logging.exception(e)
			raise MapException('Can\'t save matchsettings to \'{}\'!'.format(filename)) from e

	async def load_matchsettings(self, filename):
		"""
		Load Match Settings file and insert it into the current map playlist.

		:param filename: File to load, relative to Maps folder.
		:return: Boolean if loaded.
		"""
		try:
			if not await self._instance.storage.driver.exists(
				os.path.join(self._instance.storage.MAP_FOLDER, filename)
			):
				raise MapException('Can\'t find match settings file. Does it exist?')
			else:
				self._instance.gbx('LoadMatchSettings', filename)
		except Exception as e:
			logging.warning('Can\'t load match settings!')
			raise MapException('Can\'t load matchsettings according the dedicated server, tried loading from \'{}\'!'.format(filename)) from e
