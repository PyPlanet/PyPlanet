import asynctest

from pyplanet.core import Controller


class TestCommands(asynctest.TestCase):
	async def target(self, *args, **kwargs):
		self.target_called += 1

	async def test_registering(self):
		instance = Controller.prepare(name='default').instance
		self.target_called = 0

		from pyplanet.apps.core.maniaplanet.models import Player
		from pyplanet.contrib.command import Command

		test1 = Command(
			'test',
			self.target,
			aliases=['tst'],
			admin=False,
		)
		await instance.command_manager.register(
			test1
		)

		# Try to fetch the command.
		player = await Player.get_or_create(login='sample-1', nickname='sample-1', level=Player.LEVEL_MASTER)
		await instance.command_manager._on_chat(player, '/test', True)
		await instance.command_manager._on_chat(player, '/tst', True)

		assert self.target_called == 2
