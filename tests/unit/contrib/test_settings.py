import asynctest
import datetime

from pyplanet.contrib.setting import Setting
from pyplanet.contrib.setting.exceptions import SerializationException
from pyplanet.core import Controller


class TestSettings(asynctest.TestCase):
	async def test_registration(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()

		test_1 = Setting('test1', 'Test 1', Setting.CAT_GENERAL, type=str)
		await instance.setting_manager.register(
			test_1
		)
		setting_list = await instance.setting_manager.get_all()
		assert test_1 in setting_list

	async def test_saving(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()

		test_1 = Setting('test1', 'Test 1', Setting.CAT_GENERAL, type=str)
		await instance.setting_manager.register(
			test_1
		)

		expected = 'test1'
		await test_1.set_value('test1')
		cached = await test_1.get_value(refresh=False)
		real = await test_1.get_value(refresh=True)

		assert cached == expected
		assert real == expected

	async def test_validating(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()

		test_1 = Setting('test1', 'Test 1', Setting.CAT_GENERAL, type=str)
		await instance.setting_manager.register(
			test_1
		)

		with self.assertRaises(SerializationException) as context:
			await test_1.set_value(True)
		assert isinstance(context.exception, SerializationException)

		with self.assertRaises(SerializationException) as context:
			await test_1.set_value(1)
		assert isinstance(context.exception, SerializationException)

		with self.assertRaises(SerializationException) as context:
			await test_1.set_value(float(55))
		assert isinstance(context.exception, SerializationException)

		with self.assertRaises(SerializationException) as context:
			await test_1.set_value(dict())
		assert isinstance(context.exception, SerializationException)

		with self.assertRaises(SerializationException) as context:
			await test_1.set_value(list())
		assert isinstance(context.exception, SerializationException)

		value = test_1.get_value(refresh=True)
		assert value is not True
