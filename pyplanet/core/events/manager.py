"""
The events manager contains the class that manages custom and abstract callbacks into the system callbacks.
Once a signals is registered here it could be used by string reference. This makes it easy to have dynamically signals
being created by other apps in a single place so it could be used over all apps.

For example you would create your own custom signal if you have a app for your own created game mode script that abstracts
all the raw XML-RPC events into nice structured and maybe even including fetched data from external sources.
"""
import importlib
import logging


class _SignalManager:
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

	def register(self, signal, app=None, callback=False):
		if not getattr(signal, 'Meta', None):
			raise Exception('Signal class should have the Meta class inside.')
		if not getattr(signal.Meta, 'code', None):
			raise Exception('Signal Meta class has no code defined!')
		if not getattr(signal.Meta, 'namespace', None) and self._current_namespace:
			namespace = self._current_namespace
		elif getattr(signal.Meta, 'namespace', None):
			namespace = signal.Meta.namespace
		else:
			namespace = None  # TODO: How to handle this, will we go for the exception?
		code = signal.Meta.code

		if not hasattr(signal, 'receivers'):
			instance = signal()
		else:
			instance = signal

		signal_code = '{}:{}'.format(namespace, code)

		if callback:
			self.callbacks[code] = instance
		else:
			self.signals[signal_code] = instance

	def connect(self, signal, func, **kwargs):
		"""
		Connect to signal, or reserve it to be registerd later on.
		:param signal: Signal name.
		:param func: Function
		:param kwargs: Kwargs.
		"""
		try:
			signal = self.get_signal(signal)
			signal.connect(func, **kwargs)
		except:
			if not signal in self.reserved:
				self.reserved[signal] = list()
			self.reserved[signal].append((func, kwargs))

	def set_self(self, signal, func, slf):
		"""
		Set the self instance on a function inside of a signal.
		:param signal: Signal name.
		:param func: Function
		:param slf: Self instance reference.
		"""
		try:
			signal = self.get_signal(signal)
			signal.set_self(func, slf)
		except Exception as e:
			logging.debug(str(e))

			if signal not in self.reserved_self:
				self.reserved_self[signal] = list()
			self.reserved_self[signal].append((func, slf))

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
			raise KeyError('No such signal!')

	def finish_reservations(self):
		"""
		The method will copy all reservations to the actual signals.
		"""
		for sig_name, recs in self.reserved.items():
			for func, kwargs in recs:
				try:
					signal = self.get_signal(sig_name)
					signal.connect(func, **kwargs)
				except Exception as e:
					logging.debug(str(e))
					logging.warning('Signal not found: {}'.format(sig_name))

		for sig_name, recs in self.reserved_self.items():
			for func, slf in recs:
				try:
					signal = self.get_signal(sig_name)
					signal.set_self(func, slf)
				except Exception as e:
					logging.warning(str(e))

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

	async def finish_start(self, instance):
		"""
		Finish startup the core, this will copy reservations and fire an event.
		:param instance: Instance
		:type instance: pyplanet.core.instance.Instance
		"""
		self.finish_reservations()
		await self.get_signal('pyplanet:start').send_robust(source=dict(instance=instance))

SignalManager = _SignalManager()


def public_signal(cls):
	SignalManager.register(cls)
	return cls


def public_callback(cls):
	SignalManager.register(cls)
	return cls
