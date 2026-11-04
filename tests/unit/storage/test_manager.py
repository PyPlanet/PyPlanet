from pyplanet.core.storage import StorageDriver

from tests.base import TestCase


class TestStorageManager(TestCase):
	async def test_init(self):
		instance = self.instance
		assert instance.storage
		assert instance.storage.driver
		assert isinstance(instance.storage.driver, StorageDriver)

	async def test_driver_interface(self):
		instance = self.instance
		assert type(instance.storage.driver.openable()) is bool
