import importlib

from pyplanet.core.storage import StorageDriver, StorageInterface


class Storage(StorageInterface):

	def __init__(self, instance, driver: StorageDriver, config):
		"""
		Initiate storage manager.
		:param instance: Instance of the controller.
		:param driver: Driver instance, must be init already!
		:param config: Storage configuration (including driver + driver config).
		:type instance: pyplanet.core.instance.Instance
		:type driver: pyplanet.core.storage.StorageDriver
		:type config: dict
		"""
		self._instance = instance
		self._driver = driver
		self._config = config

	@classmethod
	def create_from_settings(cls, instance, storage_config):
		driver_path, _, driver_cls_name = storage_config['DRIVER'].rpartition('.')
		driver_options = storage_config['OPTIONS'] if 'OPTIONS' in storage_config else dict()
		driver_cls = getattr(importlib.import_module(driver_path), driver_cls_name)
		driver = driver_cls(instance, driver_options)
		return cls(instance, driver, storage_config)

	async def open(self, file: str, mode: str = 'rb'):
		pass

	async def open_matchsettings(self, file: str, mode: str = 'r'):
		pass

	async def open_map(self, file: str, mode: str = 'rb'):
		pass
