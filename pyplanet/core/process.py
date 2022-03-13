import threading
import multiprocessing

from colorlog import ColoredFormatter


def run(options):
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
		import asyncio
		import tokio
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

	# Initiate instance.
	instance = Controller.prepare(name).instance
	instance._queue = queue

	# Start and loop instance.
	instance.start()
