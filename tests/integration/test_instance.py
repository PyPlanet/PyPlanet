import asynctest

from tests.base import TestCase


class TestInstanceInit(TestCase):
	async def test_gbx_init(self):
		instance = self.instance
		await instance.gbx.connect()
		self.assertGreater(len(instance.gbx.gbx_methods), 0)
		await instance.gbx.disconnect()
		del instance

	async def test_startup(self):
		instance = self.instance
		await instance._start()
		self.assertGreater(len(instance.gbx.gbx_methods), 0)
		await instance.gbx.disconnect()
		try:
			await instance.db.engine.disconnect()
		except:
			pass
		del instance
