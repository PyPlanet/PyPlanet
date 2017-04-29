import threading

from multiprocessing import Process


def _run(name, queue):
	"""
	The actual process that runs the separate controller instance.
	
	:param name: name of the process
	:type name: str
	"""
	from pyplanet.core.instance import Controller
	import logging

	logging.getLogger(__name__).info('Starting pool process for \'{}\'...'.format(name))

	# Setting thread name to our process name.
	threading.main_thread().setName(name)

	# Start instance.
	instance = Controller.prepare(name).instance
	instance.start()


class InstanceProcess:

	def __init__(self, queue, environment_name='default', pool=None):
		"""
		Create an environment process of the controller itself.
		
		:param queue: Queue to hook on.
		:param environment_name: Name of environment.
		:param pool: Pool.
		:type queue: multiprocessing.Queue
		:type environment_name: str
		:type pool: multiprocessing.Pool
		"""
		self.queue = queue
		self.name = environment_name

		self.max_restarts = 1
		self.restarts = 0

		self.process = Process(target=_run, kwargs=dict(
			name=self.name,
			queue=self.queue
		))

		self.__last_state = True

	@property
	def did_die(self):
		if not self.is_alive() and self.__last_state:
			self.__last_state = False
			return True
		return False

	@property
	def will_restart(self):
		return self.restarts < self.max_restarts

	def is_alive(self):
		return self.process.is_alive()

	def start(self):
		return self.process.start()

	def shutdown(self):
		return self.process.terminate()
