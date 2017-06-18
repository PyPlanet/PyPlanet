import multiprocessing

import os
import time
import logging

from watchdog.observers import Observer
from logging.handlers import QueueListener

from pyplanet.utils.livereload import LiveReload
from pyplanet.god import process

logger = logging.getLogger(__name__)


class EnvironmentPool:
	"""
	This class manages the pool instances for the current environment/installation.

	.. warning::

		You should not have to use this class in any moment!

	"""

	def __init__(self, pool_names, max_restarts=0, options=None):
		self.names = pool_names
		self.queue = multiprocessing.Queue()
		self.pool = dict()
		self.max_restarts = max_restarts
		self.options = options or dict()

		self.dog_path = os.curdir
		self.dog_handler = LiveReload(self)
		# self.dog_observer = Observer()
		# self.dog_observer.schedule(self.dog_handler, self.dog_path, recursive=True)

		if multiprocessing.get_start_method() != 'fork':  # pragma: no cover
			root_logger = logging.getLogger()
			self.log_listener = QueueListener(self.queue, *root_logger.handlers)

		# TODO: Find out how to get the watchdog + livereload working on a later moment.
		# self.dog_observer.start()

		self._restarts = dict()

	def populate(self):
		"""
		Populate the pool instance processes, (prepares the processes).
		"""
		for name in self.names:
			self.pool[name] = process.InstanceProcess(queue=self.queue, environment_name=name, options=self.options)
			self._restarts[name] = 0
		return self

	def start(self):
		"""
		Start all processes.
		"""
		for name, proc in self.pool.items():
			proc.start()

	def shutdown(self):
		"""
		Shutdown all processes.
		"""

		for name, proc in self.pool.items():
			proc.shutdown()
		# self.dog_observer.stop()

	def restart(self, name=None):
		"""
		Restart single process, or all if no name is given.

		:param name: Name or none for all pools.
		"""
		if name:
			self.pool[name] = process.InstanceProcess(queue=self.queue, environment_name=name)
			self._restarts[name] += 1
			self.pool[name].start()
		else:
			for name in self.pool.keys():
				self.restart(name)

	def watchdog(self):
		"""
		Watch all the processes. (Blocking method!).
		"""
		logger.debug('Starting watchdog... watching {} instances'.format(len(self.pool)))

		while True:
			num_alive = 0
			for name, proc in self.pool.items():
				if proc.did_die:
					# Process wants a restart! = exit code 50.
					if proc.exitcode == 50:
						self.restart(name)
					# Status changed from 'online' to 'offline'
					elif self._restarts[name] < self.max_restarts:
						logger.critical('The instance \'{}\' just died. We will restart the instance!'.format(name))
						self.restart(name)
						num_alive += 1
					else:
						logger.critical('The instance \'{}\' just died. We will not restart!'.format(name))
				else:
					num_alive += 1

			# Check if there are still processes alive.
			if num_alive == 0:
				logger.critical('All instances died. Quitting now...')
				exit(1)

			time.sleep(2)
