"""
This file contains a glue between core callbacks and desired callbacks.
"""
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.events import Signal, SignalManager


class Callback(Signal):
	"""
	A callback signal is an double signal. Once for the GBX Callback itself (the Gbx callback named). And the destination
	Between those two signals is a sort of `processor` that confirms it into the PyPlanet style objects.

	For example, a player connect will result in a player database object instead of the plain Maniaplanet payload.
	This will make it possible to develop your app as fast as possible, without any overhead and make it better
	with callback payload changes!
	"""
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
		"""
		The glue method converts the source signal (gbx callback) into the pyplanet signal.
		"""
		return await self.send_robust(source)


async def handle_generic(source, signal, **kwargs):
	"""
	The handle_generic is a simple handle (`processing glue`) for just forwarding the payload from the maniaplanet
	server into the signal payload.
	"""
	if not isinstance(source, dict):
		source = dict(raw=source)
	if 'login' in source:
		try:
			if source['login']:
				source['player'] = await Player.get_by_login(source['login'])
			else:
				source['player'] = None
		except:
			source['player'] = None

	return source
