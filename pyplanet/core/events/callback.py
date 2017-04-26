"""
This file contains a glue between core callbacks and desired callbacks.
"""
from pyplanet.apps.core.maniaplanet.models import Player
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
		# Initiate destination signal (ourself).
		super().__init__(code=code, namespace=namespace, process_target=target)

		# Initiate raw signal, the raw gbx/script callback.
		self.raw_signal = Signal(code=call, namespace='raw')
		self.raw_signal.register(self.glue, weak=False)

		SignalManager.register_signal(self.raw_signal, app=None, callback=True)
		SignalManager.register_signal(self, app=None)

	async def glue(self, signal, source, **kwargs):
		return await self.send_robust(source)


async def handle_generic(source, signal, **kwargs):
	if 'login' in source:
		source['player'] = await Player.get_by_login(source['login'])
	return source
