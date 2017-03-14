from multiprocessing import Queue, Pipe
import time
import logging

from . import process

logger = logging.getLogger(__name__)


class EnvironmentPool:
	def __init__(self, pool_names, max_restarts=0):
		self.names = pool_names
		self.queue = Queue()
		self.pool = dict()
		self.max_restarts = max_restarts

		self._restarts = dict()

	def populate(self):
		for name in self.names:
			self.pool[name] = process.EnvironmentProcess(queue=self.queue, environment_name=name)
			self._restarts[name] = 0
		return self

	def start(self):
		for name, proc in self.pool.items():
			proc.process.start()

	def shutdown(self):
		for name, proc in self.pool.items():
			proc.shutdown()

	def restart(self, name):
		self.pool[name] = process.EnvironmentProcess(queue=self.queue, environment_name=name)
		self._restarts[name] += 1
		self.pool[name].start()

	def watchdog(self):
		logger.debug('Starting watchdog... watching {} instances'.format(len(self.pool)))

		while True:
			num_alive = 0
			for name, proc in self.pool.items():
				if proc.did_die:
					# Status changed from 'online' to 'offline'
					if self._restarts[name] < self.max_restarts:
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
