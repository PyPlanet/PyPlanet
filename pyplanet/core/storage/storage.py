import os

import importlib

from pyplanet.conf import settings
from pyplanet.core.storage import StorageDriver, StorageInterface


class Storage(StorageInterface):

	def __init__(self, instance, driver: StorageDriver, config):
		"""
		Initiate storage manager.
		:param instance: Instance of the controller.
		:param driver: Driver instance, must be init already!
		:param config: Storage configuration (including driver + driver config).
		:type instance: pyplanet.core.instance.Instance
		:type driver: pyplanet.core.storage.interface.StorageDriver
		:type config: dict
		"""
		self._instance = instance
		self._driver = driver
		self._config = config

		# Create temp folders for driver.
		self._tmp_root = os.path.join(settings.TMP_PATH, self._instance.process_name)
		self._tmp_driver = os.path.join(self._tmp_root, )

	@classmethod
	def create_from_settings(cls, instance, storage_config):
		driver_path, _, driver_cls_name = storage_config['DRIVER'].rpartition('.')
		driver_options = storage_config['OPTIONS'] if 'OPTIONS' in storage_config else dict()
		driver_cls = getattr(importlib.import_module(driver_path), driver_cls_name)
		driver = driver_cls(instance, driver_options)
		return cls(instance, driver, storage_config)

	@property
	def driver(self):
		"""
		Get the raw driver. Be careful with this!
		:return: Driver Instance
		:rtype: pyplanet.core.storage.interface.StorageDriver
		"""
		return self._driver

	async def open(self, file: str, mode: str = 'rb'):
		"""
		Open a file on the server. Use relative path to the dedicated root. Use the other open methods to relative
		from another base path.
		:param file: Filename/path, relative to the dedicated root path.
		:param mode: Mode to open, see the python `open` manual for supported modes.
		:return: File handler.
		:rtype: apyio.AsyncBufferedIOBaseWrapper
		"""
		return await self._driver.file(file, mode)

	async def open_match_settings(self, file: str, mode: str = 'r'):
		"""
		Open a file on the server. Relative to the MatchSettings folder (UserData/Maps/MatchSettings).
		:param file: Filename/path, relative to the dedicated matchsettings folder.
		:param mode: Mode to open, see the python `open` manual for supported modes.
		:return: File handler.
		:rtype: apyio.AsyncBufferedIOBaseWrapper
		"""
		return await self._driver.file('UserData/Maps/MatchSettings/{}'.format(file), mode)

	async def open_map(self, file: str, mode: str = 'rb'):
		"""
		Open a file on the server. Relative to the Maps folder (UserData/Maps).
		:param file: Filename/path, relative to the dedicated maps folder.
		:param mode: Mode to open, see the python `open` manual for supported modes.
		:return: File handler.
		:rtype: apyio.AsyncBufferedIOBaseWrapper
		"""
		return await self._driver.file('UserData/Maps/{}'.format(file), mode)
