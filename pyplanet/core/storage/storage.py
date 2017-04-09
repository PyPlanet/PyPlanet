import importlib

from pyplanet.core.storage import StorageDriver, StorageInterface


class Storage(StorageInterface):

	def __init__(self, instance, driver: StorageDriver, config):
		self.instance = instance
		self.driver = driver
		self.config = config

	@classmethod
	def create_from_settings(cls, instance, storage_config):
		driver_path, _, driver_cls_name = storage_config['DRIVER'].rpartition('.')
		driver_options = storage_config['OPTIONS'] if 'OPTIONS' in storage_config else dict()
		driver_cls = getattr(importlib.import_module(driver_path), driver_cls_name)
		driver = driver_cls(instance, driver_options)
		return cls(instance, driver, storage_config)
