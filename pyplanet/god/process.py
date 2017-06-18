import threading
import multiprocessing

from colorlog import ColoredFormatter


def _run(name, queue, options):
	"""
	The actual process that runs the separate controller instance.

	:param name: name of the process
	:param queue: Queue of the binding parent.
	:param options: Custom Options
	:type name: str
	"""
	from pyplanet.core.instance import Controller
	from pyplanet.utils.log import initiate_logger, QueueHandler
	import logging

	# Tokio Asyncio (EXPERIMENTAL).
	if 'tokio' in options and options['tokio'] is True:
		import tokio
		import asyncio
		policy = tokio.TokioLoopPolicy()
		asyncio.set_event_loop_policy(policy)
		asyncio.set_event_loop(tokio.new_event_loop())
		logging.warning('Using experimental Tokio Asyncio Loop!')

	# Logging to queue.
	if multiprocessing.get_start_method() != 'fork':  # pragma: no cover
		initiate_logger()
		root_logger = logging.getLogger()
		formatter = ColoredFormatter(
			'%(log_color)s%(levelname)-8s%(reset)s %(yellow)s[%(threadName)s][%(name)s]%(reset)s %(blue)s%(message)s'
		)
		queue_handler = QueueHandler(queue)
		queue_handler.setFormatter(formatter)
		root_logger.addHandler(queue_handler)

	logging.getLogger(__name__).info('Starting pool process for \'{}\'...'.format(name))

	# Setting thread name to our process name.
	threading.main_thread().setName(name)

	# Start instance.
	instance = Controller.prepare(name).instance
	instance._queue = queue
	instance.start()


class InstanceProcess:
	"""
	The InstanceProcess is the encapsulation around the real controller instance.

	.. warning::

		This code is still being executed at the main process!!

	"""

	def __init__(self, queue, environment_name='default', pool=None, options=None):
		"""
		Create an environment process of the controller itself.

		:param queue: Queue to hook on.
		:param environment_name: Name of environment.
		:param pool: Pool.
		:param options: Custom options.
		:type queue: multiprocessing.Queue
		:type environment_name: str
		:type pool: multiprocessing.Pool
		:type options: dict
		"""
		self.queue = queue
		self.name = environment_name
		self.options = options or dict()

		self.max_restarts = 1
		self.restarts = 0

		self.process = multiprocessing.Process(target=_run, kwargs=dict(
			name=self.name,
			queue=self.queue,
			options=self.options,
		))

		self.__last_state = True

	@property
	def did_die(self):
		"""
		Boolean determinating if the process did die.
		"""
		if not self.is_alive() and self.__last_state:
			self.__last_state = False
			return True
		return False

	@property
	def exitcode(self):
		"""
		Exit code of process.

		:return: Exit code.
		"""
		return self.process.exitcode

	@property
	def will_restart(self):
		"""
		Boolean: Is the process able to restart (not reached max_restarts).
		"""
		return self.restarts < self.max_restarts

	def is_alive(self):
		"""
		Call process method is_alive()
		"""
		return self.process.is_alive()

	def start(self):
		"""
		Start the process.
		"""
		return self.process.start()

	def shutdown(self):
		"""
		Shutdown (terminate) process.
		"""
		return self.process.terminate()
