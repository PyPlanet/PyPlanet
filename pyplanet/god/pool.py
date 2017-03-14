from multiprocessing import Queue, Pipe

from . import process


class EnvironmentPool:
	def __init__(self, pool_names):
		self.names = pool_names
		self.queue = Queue()
		self.pool = dict()

	def populate(self):
		for name in self.names:
			self.pool[name] = process.EnvironmentProcess(queue=self.queue, environment_name=name)
		return self

	def start(self):
		for name, proc in self.pool.items():
			proc.process.start()
