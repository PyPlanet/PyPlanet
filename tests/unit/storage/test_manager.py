import asynctest

from pyplanet.core import Controller
from pyplanet.core.storage import StorageDriver


class TestStorageManager(asynctest.TestCase):
	async def test_init(self):
		instance = Controller.prepare(name='default').instance
		assert instance.storage
		assert instance.storage.driver
		assert isinstance(instance.storage.driver, StorageDriver)

	async def test_driver_interface(self):
		instance = Controller.prepare(name='default').instance
		assert type(instance.storage.driver.openable()) is bool
