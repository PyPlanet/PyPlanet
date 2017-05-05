"""
The events manager contains the class that manages custom and abstract callbacks into the system callbacks.
Once a signals is registered here it could be used by string reference. This makes it easy to have dynamically signals
being created by other apps in a single place so it could be used over all apps.

For example you would create your own custom signal if you have a app for your own created game mode script that abstracts
all the raw XML-RPC events into nice structured and maybe even including fetched data from external sources.
"""
import importlib
import logging
import sys

from pyplanet.core.events import Signal


class _SignalManager:
	"""
	Signal Manager class.
	
	.. note::
	
		Access this via ``instance.signal_manager``.
	
	"""

	def __init__(self):
		self.signals = dict()
		self.callbacks = dict()

		# Reserved signal receivers, this will be filled, and copied to real signals later on.
		self.reserved = dict()
		self.reserved_self = dict()
		#

		self.namespaces = list()

		# This var is used to temporary override namespaces when processing apps.
		self._current_namespace = None

	def register_signal(self, signal, app=None, callback=False):
		"""
		Register a signal to be known in the signalling system.
		
		:param signal: Signal(s)
		:param app: App context/instance.
		:param callback: Will a callback handle the response (mostly raw callbacks).
		"""
		if isinstance(signal, list):
			for sig in signal:
				self.register_signal(sig)
			return

		if not signal.code:
			raise Exception('Signal code is not valid!')
		if not signal.namespace and self._current_namespace:
			namespace = self._current_namespace
		else:
			namespace = signal.namespace
		code = signal.code

		if not hasattr(signal, 'receivers'):
			instance = signal()
		else:
			instance = signal

		signal_code = '{}:{}'.format(namespace, code)

		if callback:
			self.callbacks[code] = instance
		else:
			self.signals[signal_code] = instance

	def listen(self, signal, target, conditions=None, **kwargs):
		"""
		Register a listing client to the signal given (signal instance or string).
		
		:param signal: Signal instance or string: "namespace:code"
		:param target: Target method to call.
		:param conditions: Reserved for future purposes.
		"""
		try:
			if not isinstance(signal, Signal):
				signal = self.get_signal(signal)
			signal.register(target, **kwargs)
		except:
			if signal not in self.reserved:
				self.reserved[signal] = list()
			self.reserved[signal].append((target, kwargs))

	def get_callback(self, call_name):
		"""
		Get signal by XML-RPC (script) callback.
		
		:param call_name: Callback name.
		:return: Signal class or nothing.
		:rtype: pyplanet.core.events.Signal
		"""
		if call_name in self.callbacks:
			return self.callbacks[call_name]
		logging.debug('No callback registered for {}'.format(call_name))
		return None

	def get_signal(self, key):
		"""
		Get signal by key (namespace:code).
		
		:param key: namespace:code key.
		:return: signal or none
		:rtype: pyplanet.core.events.Signal
		"""
		if key in self.signals:
			return self.signals[key]
		else:
			raise KeyError('No such signal {}!'.format(key))

	def finish_reservations(self):  # pragma: no cover
		"""
		The method will copy all reservations to the actual signals. (PRIVATE)
		"""
		for sig_name, recs in self.reserved.items():
			for func, kwargs in recs:
				try:
					signal = self.get_signal(sig_name)
					signal.connect(func, **kwargs)
				except Exception as e:
					logging.warning('Signal not found: {}, {}'.format(
						sig_name, e
					), exc_info=sys.exc_info())

		for sig_name, recs in self.reserved_self.items():
			for func, slf in recs:
				try:
					signal = self.get_signal(sig_name)
					signal.set_self(func, slf)
				except Exception as e:
					logging.warning(str(e), exc_info=sys.exc_info())

		self.reserved = dict()
		self.reserved_self = dict()

	def init_app(self, app):
		"""
		Initiate app, load all signal/callbacks files. (just import, they should register with decorators).
		
		:param app: App instance
		:type app: pyplanet.apps.AppConfig
		"""
		self._current_namespace = app.label

		# Import the signals module.
		try:
			importlib.import_module('{}.signals'.format(app.name))
		except ImportError:
			pass
		self._current_namespace = None

		# Import the callbacks module.
		try:
			importlib.import_module('{}.callbacks'.format(app.name))
		except ImportError:
			pass

	async def finish_start(self, *args, **kwargs):
		"""
		Finish startup the core, this will copy reservations. (PRIVATE).
		"""
		self.finish_reservations()

SignalManager = _SignalManager()


def public_signal(cls):
	SignalManager.register_signal(cls)
	return cls


def public_callback(cls):
	SignalManager.register_signal(cls)
	return cls
