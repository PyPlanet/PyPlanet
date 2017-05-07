import asynctest

from pyplanet.core import Controller


class TestCommands(asynctest.TestCase):
	async def target(self, *args, **kwargs):
		self.target_called += 1

	async def num_target(self, player, data, **kwargs):
		self.target_called += len(data.numbers)

	async def test_registering(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

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
		player, _ = await Player.get_or_create(login='sample-1', nickname='sample-1', level=Player.LEVEL_MASTER)
		await instance.command_manager._on_chat(player, '/test', True)
		await instance.command_manager._on_chat(player, '/tst', True)

		assert self.target_called == 2

	async def test_params(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

		self.target_called = 0

		from pyplanet.apps.core.maniaplanet.models import Player
		from pyplanet.contrib.command import Command

		test1 = Command(
			'test',
			self.target,
			aliases=['tst'],
			admin=False,
		).add_param('test', type=str, required=True)
		test2 = Command(
			'test2',
			self.num_target,
			admin=True,
		).add_param('numbers', type=int, nargs='*', required=True)
		await instance.command_manager.register(
			test1, test2
		)

		# Try to fetch the command.
		player, _ = await Player.get_or_create(login='sample-1', nickname='sample-1', level=Player.LEVEL_MASTER)
		await instance.command_manager._on_chat(player, '/test ok', True)
		await instance.command_manager._on_chat(player, '/tst okok', True)

		assert self.target_called == 2
		self.target_called = 0

		await instance.command_manager._on_chat(player, '//test2 1 2 3 4 5', True)
		await instance.command_manager._on_chat(player, '/admin test2 4 5', True)

		assert self.target_called == 7
