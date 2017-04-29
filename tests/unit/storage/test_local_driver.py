import os
import asynctest

from pyplanet.core import Controller


class TestStorageManager(asynctest.TestCase):

	def __init__(self, *args, **kwargs):
		from pyplanet.conf import settings
		self.tmp_dir = settings.TMP_PATH
		self.tmp_file = os.path.join(self.tmp_dir, 'test-{}.txt'.format(id(self)))
		self.instance = Controller.prepare(name='default').instance
		super().__init__(*args, **kwargs)

	async def test_init(self):
		assert self.instance.storage.driver

	async def test_exists(self):
		assert await self.instance.storage.driver.exists(__file__) is True

	async def test_touch(self):
		await self.instance.storage.driver.touch(self.tmp_file)
		assert await self.instance.storage.driver.exists(self.tmp_file) is True
		await self.instance.storage.driver.remove(self.tmp_file)
		assert await self.instance.storage.driver.exists(self.tmp_file) is False

	async def test_remove(self):
		await self.instance.storage.driver.touch(self.tmp_file)
		assert await self.instance.storage.driver.exists(self.tmp_file) is True
		await self.instance.storage.driver.remove(self.tmp_file)
		assert await self.instance.storage.driver.exists(self.tmp_file) is False

	async def test_open_read_write(self):
		await self.instance.storage.driver.touch(self.tmp_file)

		async with self.instance.storage.driver.open(self.tmp_file, 'w') as fh:
			await fh.write('Test OK')

		async with self.instance.storage.driver.open(self.tmp_file) as fh:
			assert await fh.read() == 'Test OK'

		await self.instance.storage.driver.remove(self.tmp_file)
