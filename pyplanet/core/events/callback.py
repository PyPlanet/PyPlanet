"""
This file contains a glue between core callbacks and desired callbacks.
"""
from pyplanet.core.events import Signal, SignalManager


class Callback(Signal):
	def __init__(self, call, namespace, code, target=None):
		"""
		Shortcut for registering two signals, one is the raw signal and the second one is the parsed and structured
		output signal. This also glues the two together.
		:param call:
		:param namespace:
		:param code:
		:param target:
		"""
		super().__init__()
		self.raw_signal = Signal()
		self.raw_signal.Meta.code = call
		self.raw_signal.Meta.namespace = 'raw'
		self.raw_signal.connect(self.glue, weak=False)
		SignalManager.register(self.raw_signal, app=None, callback=True)

		self.Meta.code = code
		self.Meta.namespace = namespace
		self.process_target = target
		SignalManager.register(self, app=None)

	async def glue(self, signal, source, **kwargs):
		return await self.send_robust(source)
