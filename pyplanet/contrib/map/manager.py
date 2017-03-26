import asyncio

from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Map
from pyplanet.contrib.map.exceptions import MapNotFound
from pyplanet.core.events import receiver
from pyplanet.core import signals


class MapManager:
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		# The matchsettings contains the name of the current loaded matchsettings file.
		self._matchsettings = None

		# The maps contain a list of map instances in the order that are in the current loaded list.
		self._maps = set()

		# The current map will always be in this variable. The next map will always be here. It will be updated. once
		# it's updated it should be send to the dedicated to queue the next map.
		self._current_map = None
		self._next_map = None

		# Initiate the self instances on receivers.
		self.handle_startup()

	@receiver(signals.pyplanet_start_apps_before)
	async def handle_startup(self, **kwargs):
		# Fetch the list of maps.
		raw_list = await self._instance.gbx.execute('GetMapList', -1, 0)

		# We will initiate the maps in the database (or update).
		for details in raw_list:
			map = await Map.get_or_create_from_info(
				details['UId'], details['FileName'], details['Name'], details['Author'],
				environment=details['Environnement'], time_gold=details['GoldTime'],
				price=details['CopperPrice'], map_type=details['MapType'], map_style=details['MapStyle']
			)

			self._maps.add(map)

		# Get current and next map.
		self._current_map, self._next_map = await asyncio.gather(
			self.handle_map_change(await self._instance.gbx.execute('GetCurrentMapInfo')),
			self.handle_map_change(await self._instance.gbx.execute('GetNextMapInfo')),
		)

	async def handle_map_change(self, info):
		"""
		This will be called from the glue that creates the signal 'maniaplanet:map_begin' or 'map_end'.
		:param info: Mapinfo in dict.
		:return: Map instance.
		:rtype: pyplanet.apps.core.maniaplanet.models.map.Map
		"""
		return await Map.get_or_create_from_info(
			uid=info['UId'], name=info['Name'], author_login=info['Author'], file=info['FileName'],
			environment=info['Environnement'], map_type=info['MapType'], map_style=info['MapStyle'],
			num_laps=info['NbLaps'], num_checkpoints=info['NbCheckpoints'], time_author=info['AuthorTime'],
			time_bronze=info['BronzeTime'], time_silver=info['SilverTime'], time_gold=info['GoldTime'],
			price=info['CopperPrice']
		)

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

	@property
	def next_map(self):
		return self._next_map

	async def set_next_map(self, map):
		if isinstance(map, str):
			map = await self.get_map(map)
		if not isinstance(map, Map):
			raise Exception('When setting the map, you should give an Map instance!')
		await self._instance.gbx.execute('SetNextMapIdent', map.uid)
		self._next_map = map

	@property
	def current_map(self):
		return self._current_map

	async def set_current_map(self, map):
		"""
		Set the current map and jump to it.
		:param map: Map instance or uid.
		"""
		if isinstance(map, str):
			map = await self.get_map(map)
		if not isinstance(map, Map):
			raise Exception('When setting the map, you should give an Map instance!')

		await self._instance.gbx.execute('JumpToMapIdent', map.uid)
		self._next_map = map
