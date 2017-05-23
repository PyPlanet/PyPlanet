"""
This file has been forked from Django and PyDispatcher.
The PyDispatcher is licensed under BSD.
"""
import threading
import weakref
import logging
import asyncio

from pyplanet.core.exceptions import SignalException, SignalGlueStop
from pyplanet.utils.log import handle_exception


def _make_id(target):
	if hasattr(target, '__func__'):
		return id(target.__self__), id(target.__func__)
	return id(target)


NONE_ID = _make_id(None)
NO_RECEIVERS = object()

logger = logging.getLogger(__name__)


class Signal:
	"""
	A signal is a destination tho distribute to where multiple listeners get the message. (event distribution).
	"""

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
			self.code = code
		else:
			self.code = self.Meta.code

		if namespace:
			self.namespace = namespace
		else:
			self.namespace = self.Meta.namespace

		self.use_caching = use_caching
		self.sender_receivers_cache = weakref.WeakKeyDictionary() if use_caching else {}
		self._dead_receivers = False

	class Meta:
		"""
		The meta-class contains the code of the signal, used for string notation.
		An optional namespace could be given to override the app label namespace.

		.. warning::

			Only change or access this if you override the ``Signal`` class in your own class.

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

	def set_self(self, receiver, slf):  # pragma: no cover
		"""
		Set the self instance on a receiver.

		.. deprecated:: 0.0.1

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

	def register(self, receiver, weak=True, dispatch_uid=None):
		"""
		Connect receiver to sender for signal.

		:param receiver: A function or an instance method which is to receive signals. Receivers must be hashable objects.
			If weak is True, then receiver must be weak referenceable.Receivers must be able to accept keyword arguments.
			If a receiver is connected with a dispatch_uid argument, it
			will not be added if another receiver was already connected with that dispatch_uid.

		:param weak: Whether to use weak references to the receiver. By default, the
			module will attempt to use weak references to the receiver
			objects. If this parameter is false, then strong references will
			be used.

		:param dispatch_uid: An identifier used to uniquely identify a particular instance of
			a receiver. This will usually be a string, though it may be anything hashable.
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

	def unregister(self, receiver=None, dispatch_uid=None):
		"""
		Disconnect receiver from sender for signal.
		If weak references are used, disconnect need not be called. The receiver
		will be removed from dispatch automatically.

		:param receiver: The registered receiver to disconnect. May be none if dispatch_uid is specified.
		:param dispatch_uid: the unique identifier of the receiver to disconnect
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

	@staticmethod
	async def execute_receiver(receiver, args, kwargs, ignore_exceptions=False):
		try:
			if asyncio.iscoroutinefunction(receiver):
				if len(args) > 0:
					return receiver, await receiver(*args, **kwargs)
				return receiver, await receiver(**kwargs)

			if len(args) > 0:
				return receiver, receiver(*args, **kwargs)
			return receiver, receiver(**kwargs)
		except Exception as exc:
			if not ignore_exceptions:
				raise

			logger.exception(SignalException(
				'Signal receiver \'{}\' => {} thrown an exception!'.format(receiver.__module__, receiver.__name__)
			), exc_info=False)

			# Handle, will send to sentry if it's related to the core/contrib apps.
			handle_exception(exc, receiver.__module__, receiver.__name__)

			# Log the actual exception.
			logger.exception(exc)
			return receiver, exc

	async def send(self, source, raw=False, catch_exceptions=False, gather=True):
		"""
		Send signal with source.
		If any receiver raises an error, the error propagates back through send,
		terminating the dispatch loop. So it's possible that all receivers
		won't be called if an error is raised.

		:param source: The data to be send to the processor which produces data that will be send to the receivers.
		:param raw: Optional bool parameter to just send the source to the receivers without any processing.
		:param catch_exceptions: Catch and return the exceptions.
		:param gather: Execute multiple receivers at the same time (parallel). On by default!

		:return: Return a list of tuple pairs [(receiver, response), ... ].
		"""
		if raw is False:
			try:
				kwargs = await self.process_target(signal=self, source=source)
			except SignalGlueStop:
				# Stop calling the receivers when our glue says we should!
				return []
		else:
			kwargs = dict(**source, signal=self)

		if not self.receivers:
			return []

		# Prepare the responses from the calls.
		responses = []
		gather_list = []
		for key, receiver in self._live_receivers():
			# Dereference the weak reference.
			slf = self.self_refs.get(key, None)
			if slf and isinstance(slf, weakref.ReferenceType):
				slf = slf()
			args = [slf] if slf else []

			# Execute the receiver.
			coro = self.execute_receiver(receiver, args, kwargs, ignore_exceptions=catch_exceptions)
			if gather:
				gather_list.append(coro)
			else:
				responses.append(await coro)

		# If gather, wait on the asyncio.gather operation and return the responses from there.
		if gather:
			return await asyncio.gather(*gather_list)

		# Done, respond with all the results
		return responses

	async def send_robust(self, source=None, raw=False, gather=True):
		"""
		Send signal from sender to all connected receivers catching errors.

		:param source: The data to be send to the processor which produces data that will be send to the receivers.
		:param raw: Optional bool parameter to just send the source to the receivers without any processing.
		:param gather: Execute multiple receivers at the same time (parallel). On by default!

		:return: Return a list of tuple pairs [(receiver, response), ... ].
			If any receiver raises an error (specifically any subclass of Exception),
			return the error instance as the result for that receiver.
		"""
		return await self.send(source, raw, catch_exceptions=True, gather=gather)

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
