import asynctest
import datetime

from pyplanet.core import Controller


class TestPermissions(asynctest.TestCase):
	async def test_registration(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()

		from pyplanet.apps.core.maniaplanet.models import Player
		await instance.permission_manager.register(
			'test1',
			namespace='tst1',
			min_level=Player.LEVEL_PLAYER
		)
		assert bool(await instance.permission_manager.get_perm('tst1', 'test1'))

	async def test_checking(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

		from pyplanet.apps.core.maniaplanet.models import Player
		await instance.permission_manager.register(
			'sample1',
			namespace='tst1',
			min_level=Player.LEVEL_PLAYER
		)
		await instance.permission_manager.register(
			'sample2',
			namespace='tst1',
			min_level=Player.LEVEL_OPERATOR
		)
		await instance.permission_manager.register(
			'sample3',
			namespace='tst1',
			min_level=Player.LEVEL_ADMIN
		)
		await instance.permission_manager.register(
			'sample4',
			namespace='tst1',
			min_level=Player.LEVEL_MASTER
		)

		# Try to fetch the command.
		try:
			player1 = await Player.get(login='sample-1')
		except:
			player1 = await Player.create(login='sample-1', nickname='sample-1', level=Player.LEVEL_MASTER)
		try:
			player2 = await Player.get(login='sample-2')
		except:
			player2 = await Player.create(login='sample-2', nickname='sample-2', level=Player.LEVEL_PLAYER)

		assert await instance.permission_manager.has_permission(player1, 'tst1:sample1')
		assert await instance.permission_manager.has_permission(player1, 'tst1:sample2')
		assert await instance.permission_manager.has_permission(player1, 'tst1:sample3')
		assert await instance.permission_manager.has_permission(player1, 'tst1:sample4')

		assert await instance.permission_manager.has_permission(player2, 'tst1:sample1')
		assert not await instance.permission_manager.has_permission(player2, 'tst1:sample2')
		assert not await instance.permission_manager.has_permission(player2, 'tst1:sample3')
		assert not await instance.permission_manager.has_permission(player2, 'tst1:sample4')
