import asynctest

from pyplanet.apps import AppConfig
from pyplanet.core import Controller
from pyplanet.core.events import Signal


class TestSignals(asynctest.TestCase):
	async def test_registering(self):
		instance = Controller.prepare(name='default').instance

		test1 = Signal(code='test1', namespace='tests')
		instance.signals.register_signal(test1)
		test2 = Signal(code='test2', namespace='tests')
		instance.signals.register_signal(test2)

		test1_comp = instance.signals.get_signal('tests:test1')
		test2_comp = instance.signals.get_signal('tests:test2')

		assert test1 == test1_comp
		assert test2 == test2_comp

	async def test_listening(self):
		instance = Controller.prepare(name='default').instance

		test1 = Signal(code='test1', namespace='tests', process_target=self.glue)
		instance.signals.register_signal(test1)

		self.got_sync = 0
		self.got_async = 0
		self.got_glue = 0
		self.got_raw = 0

		test1.register(self.sync_listener)
		test1.register(self.async_listener)

		await test1.send(dict(glue=False), raw=True)
		await test1.send(dict(glue=False), raw=False)
		await test1.send_robust(dict(glue=False), raw=True)
		await test1.send_robust(dict(glue=False), raw=False)

		assert self.got_async == 4
		assert self.got_sync == 4
		assert self.got_glue == 2
		assert self.got_raw == 4

	async def test_unregister(self):
		instance = Controller.prepare(name='default').instance
		test1 = Signal(code='test1', namespace='tests', process_target=self.glue)
		instance.signals.register_signal(test1)

		self.got_sync = 0
		self.got_async = 0
		self.got_glue = 0
		self.got_raw = 0

		test1.register(self.sync_listener)
		test1.register(self.async_listener)

		await test1.send(dict(glue=False))

		# Unregister + send
		test1.unregister(self.sync_listener)

		await test1.send(dict(glue=False), raw=True)

		assert self.got_sync == 1
		assert self.got_async == 2

	async def test_app_manager(self):
		instance = Controller.prepare(name='default').instance
		manager = instance.signals.create_app_manager(None)

		test1 = Signal(code='test1', namespace='tests', process_target=self.glue)
		manager.register_signal(test1)

		self.got_sync = 0
		self.got_async = 0
		self.got_glue = 0
		self.got_raw = 0

		manager.listen(test1, self.sync_listener)
		manager.listen(test1, self.async_listener)

		await test1.send(dict(glue=False))

		await manager.on_destroy()

		# This one will be ignored because the app is destroyed.
		await test1.send(dict(glue=False), raw=True)

		assert self.got_sync == 1
		assert self.got_async == 1

	####################################################################################################################

	def sync_listener(self, glue=None, source=None, **kwargs):
		self.got_sync += 1
		if glue is not True:
			self.got_raw += 1
		if source:
			assert isinstance(source, dict)

	async def async_listener(self, glue=None, source=None, **kwargs):
		self.got_async += 1
		if glue is not True:
			self.got_raw += 1
		if source:
			assert isinstance(source, dict)

	async def glue(self, source, signal):
		self.got_glue += 1
		return dict(glue=True)
