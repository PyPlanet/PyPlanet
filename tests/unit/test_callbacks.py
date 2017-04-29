import asynctest

from pyplanet.core import Controller
from pyplanet.core.events import Signal, Callback


class TestCallbacks(asynctest.TestCase):
	async def test_registering(self):
		instance = Controller.prepare(name='default').instance

		test1 = Callback(
			call='SampleCall',
			code='sample_call',
			namespace='tests',
			target=self.handle_sample
		)

		test1_comp = instance.signal_manager.get_callback('SampleCall')

		assert test1.raw_signal == test1_comp

	async def test_listening(self):
		test1 = Callback(
			call='SampleCall',
			code='sample_call',
			namespace='tests',
			target=self.handle_sample
		)

		self.got_sync = 0
		self.got_async = 0
		self.got_handle = 0
		self.got_glue = 0

		test1.register(self.sync_listener)
		test1.register(self.async_listener)

		await test1.raw_signal.send(dict(glue=False), raw=False)
		await test1.raw_signal.send_robust(dict(glue=False), raw=False)

		assert self.got_async == 2
		assert self.got_sync == 2
		assert self.got_glue == 0
		assert self.got_handle == 2

	####################################################################################################################

	def sync_listener(self, *args, **kwargs):
		self.got_sync += 1

	async def async_listener(self, *args, **kwargs):
		self.got_async += 1

	async def glue(self, *args, **kwargs):
		self.got_glue += 1
		return dict(glue=True)

	async def handle_sample(self, *args, **kwargs):
		self.got_handle += 1
		return dict(handle=True)
