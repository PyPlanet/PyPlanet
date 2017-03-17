"""
This file has been forked from Django and PyDispatcher.
The PyDispatcher is licensed under BSD.
"""

import threading
import weakref


def _make_id(target):
	if hasattr(target, '__func__'):
		return id(target.__self__), id(target.__func__)
	return id(target)


NONE_ID = _make_id(None)
NO_RECEIVERS = object()


class Signal:
	def __init__(self, process_target=None, use_caching=False):
		"""
		Create a new signal.
		"""
		if not process_target:
			process_target = self.process
		self.process_target = process_target

		#
		self.receivers = list()
		self.lock = threading.Lock()

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

	def process(self, raw):
		"""
		This method processed data into abstract data. You can give your own function in the init of the Signal or
		override the method.
		:param raw: Raw data input
		:return: Parsed data output
		"""
		return raw

	def has_listeners(self):
		"""
		Has the signal listeners.
		:return:
		"""
		return bool(self._live_receivers())

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
					break
			self.sender_receivers_cache.clear()

		return disconnected

	def send(self, source, raw=False):
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
		if not self.receivers:
			return []

		if not raw:
			source = self.process_target(source)

		return [
			(receiver, receiver(signal=self, source=source))
			for receiver in self._live_receivers()
			]

	def send_robust(self, source, raw=False):
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
		if not self.receivers:
			return []

		# Call each receiver with whatever arguments it can accept.
		# Return a list of tuple pairs [(receiver, response), ... ].
		responses = []
		for receiver in self._live_receivers():
			try:
				if not raw:
					source = self.process_target(source)

				response = receiver(signal=self, source=source)
			except Exception as err:
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
				senderkey = _make_id(sender)
				receivers = []
				for (receiverkey, r_senderkey), receiver in self.receivers:
					if r_senderkey == NONE_ID or r_senderkey == senderkey:
						receivers.append(receiver)
				if self.use_caching:
					if not receivers:
						self.sender_receivers_cache[sender] = NO_RECEIVERS
					else:
						# Note, we must cache the weakref versions.
						self.sender_receivers_cache[sender] = receivers
		non_weak_receivers = []
		for receiver in receivers:
			if isinstance(receiver, weakref.ReferenceType):
				# Dereference the weak reference.
				receiver = receiver()
				if receiver is not None:
					non_weak_receivers.append(receiver)
			else:
				non_weak_receivers.append(receiver)
		return non_weak_receivers

	def _remove_receiver(self):
		# The list must be marked as dead. And will be cleaned in the next registry or call.
		# We can't directly remove because GC is always running when lock is preserved.
		self._dead_receivers = True


def receiver(signal, **kwargs):
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
	:param kwargs:
	:return:
	"""
	def connect(signal, func, **kwargs):
		if type(signal) is str:
			# Try to fetch signal from manager.
			# TODO:
			pass
		elif isinstance(signal, Signal):
			signal.connect(func, **kwargs)
		raise Exception('Signal should be a valid string or signal instance. or a tuple/list with multiple.')

	def decorator(func):
		if isinstance(signal, (list, tuple)):
			for sig in signal:
				connect(sig, func, **kwargs)
		else:
			connect(signal, func, **kwargs)
		return func

	return decorator
