import os
import asynctest

from pyplanet.core import Controller


class TestStorageManager(asynctest.TestCase):

	def __init__(self, *args, **kwargs):
		from pyplanet.conf import settings
		self.tmp_dir = settings.TMP_PATH
		self.tmp_file = os.path.join(self.tmp_dir, 'test-{}'.format(id(self)))
		self.instance = Controller.prepare(name='default').instance
		super().__init__(*args, **kwargs)

	async def test_init(self):
		assert self.instance.storage.driver

	async def test_exists(self):
		assert await self.instance.storage.driver.exists(__file__) is True

	async def test_touch(self):
		file = '{}-1.txt'.format(self.tmp_file)
		await self.instance.storage.driver.touch(file)
		assert await self.instance.storage.driver.exists(file) is True
		await self.instance.storage.driver.remove(file)
		assert await self.instance.storage.driver.exists(file) is False

	async def test_remove(self):
		file = '{}-2.txt'.format(self.tmp_file)
		await self.instance.storage.driver.touch(file)
		assert await self.instance.storage.driver.exists(file) is True
		await self.instance.storage.driver.remove(file)
		assert await self.instance.storage.driver.exists(file) is False

	async def test_open_read_write(self):
		file = '{}-3.txt'.format(self.tmp_file)
		await self.instance.storage.driver.touch(file)

		async with self.instance.storage.driver.open(file, 'w') as fh:
			await fh.write('Test OK')

		async with self.instance.storage.driver.open(file) as fh:
			assert await fh.read() == 'Test OK'
