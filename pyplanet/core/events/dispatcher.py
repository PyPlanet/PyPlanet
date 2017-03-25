"""
This file has been forked from Django and PyDispatcher.
The PyDispatcher is licensed under BSD.
"""

import threading
import weakref
import logging
import asyncio

from pyplanet.core.events.manager import SignalManager
from pyplanet.core.exceptions import SignalException


def _make_id(target):
	if hasattr(target, '__func__'):
		return id(target.__self__), id(target.__func__)
	return id(target)


NONE_ID = _make_id(None)
NO_RECEIVERS = object()

logger = logging.getLogger(__name__)


class Signal:
	def __init__(self, code=None, namespace=None, process_target=None, use_caching=False):
		"""
		Create a new signal.
		"""
		if not process_target:
			process_target = self.process
		self.process_target = process_target

		self.receivers = list()
		self.self_refs = dict()
		self.lock = threading.Lock()

		if code:
			self.Meta.code = code
		if namespace:
			self.Meta.namespace = namespace

		self.use_caching = use_caching
		self.sender_receivers_cache = weakref.WeakKeyDictionary() if use_caching else {}
		self._dead_receivers = False

	class Meta:
		"""
		The meta-class contains the code of the signal, used for string notation.
		An optional namespace could be given to override the app label namespace.
		"""
		code = None
		namespace = None

	async def process(self, **data):
		"""
		This method processed data into abstract data. You can give your own function in the init of the Signal or
		override the method.
		:param data: Raw data input
		:return: Parsed data output
		"""
		return data

	def has_listeners(self):
		"""
		Has the signal listeners.
		:return:
		"""
		return bool(self._live_receivers())

	def set_self(self, receiver, slf):
		"""
		Set the self instance on a receiver.
		:param receiver: Receiver function.
		:param slf: Self instance
		"""
		with self.lock:
			lookup_key = _make_id(receiver)
			for key, _ in self.receivers:
				if lookup_key == key:
					ref = weakref.ref
					slf = ref(slf)
					self.self_refs[lookup_key] = slf
					return
			raise Exception('Receiver is not yet known! You registered too early!')

	def connect(self, receiver, weak=True, dispatch_uid=None):
		"""
		Connect receiver to sender for signal.
		Arguments:
			receiver
				A function or an instance method which is to receive signals.
				Receivers must be hashable objects.
				If weak is True, then receiver must be weak referenceable.
				Receivers must be able to accept keyword arguments.
				If a receiver is connected with a dispatch_uid argument, it
				will not be added if another receiver was already connected
				with that dispatch_uid.
			weak
				Whether to use weak references to the receiver. By default, the
				module will attempt to use weak references to the receiver
				objects. If this parameter is false, then strong references will
				be used.
			dispatch_uid
				An identifier used to uniquely identify a particular instance of
				a receiver. This will usually be a string, though it may be
				anything hashable.
		"""
		if dispatch_uid:
			lookup_key = dispatch_uid
		else:
			lookup_key = _make_id(receiver)

		if weak:
			ref = weakref.ref
			receiver_object = receiver

			# Check for bound methods.
			if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
				ref = weakref.WeakMethod
				receiver_object = receiver.__self__
			receiver = ref(receiver)
			weakref.finalize(receiver_object, self._remove_receiver)

		with self.lock:
			self._clear_dead_receivers()
			for rec_key in self.receivers:
				if rec_key == lookup_key:
					break
			else:
				self.receivers.append((lookup_key, receiver))
			self.sender_receivers_cache.clear()

	def disconnect(self, receiver=None, dispatch_uid=None):
		"""
		Disconnect receiver from sender for signal.
		If weak references are used, disconnect need not be called. The receiver
		will be removed from dispatch automatically.
		Arguments:
			receiver
				The registered receiver to disconnect. May be none if
				dispatch_uid is specified.
			dispatch_uid
				the unique identifier of the receiver to disconnect
		"""
		if dispatch_uid:
			lookup_key = dispatch_uid
		else:
			lookup_key = _make_id(receiver)

		disconnected = False
		with self.lock:
			self._clear_dead_receivers()
			for index in range(len(self.receivers)):
				(rec_key, _) = self.receivers[index]
				if rec_key == lookup_key:
					disconnected = True
					del self.receivers[index]
					if rec_key in self.self_refs:
						del self.self_refs[rec_key]
					break
			self.sender_receivers_cache.clear()

		return disconnected

	async def send(self, source, raw=False):
		"""
		Send signal with source.
		If any receiver raises an error, the error propagates back through send,
		terminating the dispatch loop. So it's possible that all receivers
		won't be called if an error is raised.
		Arguments:
			source
				The data to be send to the processor which produces data
				that will be send to the receivers.
			raw
				Optional bool parameter to just send the source to the receivers without
				any processing.

		Return a list of tuple pairs [(receiver, response), ... ].
		"""
		if not isinstance(source, dict):
			source = dict(source=source)

		if not raw:
			source = await self.process_target(**source)

		if not self.receivers:
			return []

		source['signal'] = self

		# Call each receiver with whatever arguments it can accept.
		# Return a list of tuple pairs [(receiver, response), ... ].
		responses = []
		for key, receiver in self._live_receivers():
			slf = self.self_refs.get(key, None)

			if slf and isinstance(slf, weakref.ReferenceType):
				# Dereference the weak reference.
				slf = slf()

				if asyncio.iscoroutinefunction(receiver):
					response = await receiver(slf, **source)
				else:
					response = receiver(slf, **source)
			else:
				if asyncio.iscoroutinefunction(receiver):
					response = await receiver(**source)
				else:
					response = receiver(**source)

			responses.append((receiver, response))
		return responses

	async def send_robust(self, source=None, raw=False):
		"""
		Send signal from sender to all connected receivers catching errors.
		Arguments:
			source
				The data to be send to the processor which produces data
				that will be send to the receivers.
			raw
				Optional bool parameter to just send the source to the receivers without
				any processing.

		Return a list of tuple pairs [(receiver, response), ... ].
		If any receiver raises an error (specifically any subclass of
		Exception), return the error instance as the result for that receiver.
		"""
		if not isinstance(source, dict):
			source = dict(source=source)

		if not raw:
			source = await self.process_target(**source)

		if not self.receivers:
			return []

		source['signal'] = self

		# Call each receiver with whatever arguments it can accept.
		# Return a list of tuple pairs [(receiver, response), ... ].
		responses = []
		for key, receiver in self._live_receivers():
			try:
				slf = self.self_refs.get(key, None)
				if slf and isinstance(slf, weakref.ReferenceType):
					# Dereference the weak reference.
					slf = slf()

					if asyncio.iscoroutinefunction(receiver):
						response = await receiver(slf, **source)
					else:
						response = receiver(slf, **source)
				else:
					if asyncio.iscoroutinefunction(receiver):
						response = await receiver(**source)
					else:
						response = receiver(**source)
			except Exception as err:
				logger.exception(SignalException(
					'Signal receiver \'{}\' => {} thrown an exception!'.format(receiver.__module__, receiver.__name__)
				))
				logger.exception(err)
				responses.append((receiver, err))
			else:
				responses.append((receiver, response))
		return responses

	def _clear_dead_receivers(self):
		if self._dead_receivers:
			self._dead_receivers = False
			new_receivers = []
			for rec in self.receivers:
				if isinstance(rec[1], weakref.ReferenceType) and rec[1]() is None:
					continue
				new_receivers.append(rec)
			self.receivers = new_receivers

	def _live_receivers(self):
		"""
		Filter sequence of receivers to get resolved, live receivers.
		This checks for weak references and resolves them, then returning only
		live receivers.
		"""
		# We don't use the sender. Set it to none.
		sender = None

		receivers = None
		if self.use_caching and not self._dead_receivers:
			receivers = self.sender_receivers_cache.get(sender)
			# We could end up here with NO_RECEIVERS even if we do check this case in
			# .send() prior to calling _live_receivers() due to concurrent .send() call.
			if receivers is NO_RECEIVERS:
				return []

		if receivers is None:
			with self.lock:
				self._clear_dead_receivers()
				receivers = []
				for receiverkey, receiver in self.receivers:
					receivers.append((receiverkey, receiver))
				if self.use_caching:
					if not receivers:
						self.sender_receivers_cache[sender] = NO_RECEIVERS
					else:
						# Note, we must cache the weakref versions.
						self.sender_receivers_cache[sender] = receivers
		non_weak_receivers = []

		for receiver in receivers:
			key = receiver[0]
			receiver = receiver[1]

			if isinstance(receiver, weakref.ReferenceType):
				# Dereference the weak reference.
				receiver = receiver()
				if receiver is not None:
					non_weak_receivers.append((key, receiver))
			else:
				non_weak_receivers.append((key, receiver))
		return non_weak_receivers

	def _remove_receiver(self):
		# The list must be marked as dead. And will be cleaned in the next registry or call.
		# We can't directly remove because GC is always running when lock is preserved.
		self._dead_receivers = True


def receiver(signal, filter=None, **kwargs):
	"""
	Decorator for registering a receiver for a specific signal::

		@receiver(signals.player_connect)
		def player_connect(**kwargs):
			print(kwargs.get('player'))
			...

		@receiver('maniaplanet.custom-signal')
		def custom(**kwargs):
			...

		# This example is strongly not advised. Instead, please register your custom signal and abstraction!
		@receiver('raw.LibXmlRpc_BeginRoundStop')
		def custom(**kwargs):
			...

	:param signal: Signal string or identifier.
	:param filter: Filter of the contents. Not yet implemented ()
	:param kwargs:
	"""
	def connect(func):
		if isinstance(signal, Signal):
			signal.connect(func, **kwargs)
		elif isinstance(signal, str):
			try:
				SignalManager.connect(signal, func, **kwargs)
			except Exception as e:
				logger.debug(str(e))
		else:
			raise Exception('Signal should be a valid string or signal instance. or a tuple/list with multiple.')

	def set_self(func, self):
		if isinstance(signal, Signal):
			signal.set_self(func, self)
		elif isinstance(signal, str):
			try:
				SignalManager.set_self(signal, func, self)
			except Exception as e:
				logger.debug(str(e))
		else:
			raise Exception('Signal should be a valid string or signal instance. or a tuple/list with multiple.')

	def decorator(func):
		# If signal is an array of signals/strings, loop and connect. If not, just connect the single one.
		if isinstance(signal, (list, tuple)):
			for sig in signal:
				connect(func)
		else:
			connect(func)

		def wrapper(*ag, **kw):
			try:
				# When only one argument given and it contains the __dict__ we have the registering self call.
				# At this point, we want to set the self instance into our signal instance and pass away the call.
				if len(ag) == 1 and hasattr(ag[0], '__dict__'):
					set_self(func, ag[0])
				else:
					# Mostly we really want to call it. Throw exception for flow control.
					raise Exception()
			except:
				# Call the real function.
				return func(*ag, **kw)
		return wrapper
	# TODO: Filter signal
	return decorator
