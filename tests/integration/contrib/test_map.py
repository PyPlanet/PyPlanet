import asyncio
import os

import asynctest

from pyplanet.core.instance import Controller


class TestMapManager(asynctest.TestCase):
	async def test_map_list(self):
		instance = Controller.prepare(name='default').instance
		await instance._start()

		real_list = await instance.gbx.execute('GetMapList', -1, 0)

		assert len(real_list) == len(instance.map_manager.maps)

		await instance.gbx.disconnect()
		del instance
