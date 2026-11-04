import asynctest

from pyplanet.core import Controller
from pyplanet.core.instance import Instance


class TestCase(asynctest.TestCase):
	instance: Instance

	async def setUpController(self):
		self.instance = Controller.prepare(name='default').instance

	async def tearDownController(self):
		await self.instance.db.disconnect()

	async def setUp(self):
		await self.setUpController()

	async def tearDown(self):
		await self.tearDownController()
