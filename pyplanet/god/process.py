from multiprocessing import Process

import asyncio


class EnvironmentProcess:

	def __init__(self, queue, environment_name='default'):
		"""
		Create an environment process of the controller itself.
		:param queue: Queue to hook on.
		:param environment_name: Name of environment.
		:type queue: multiprocessing.Queue
		:type environment_name: str
		"""
		self.queue = queue
		self.name = environment_name
		self.loop = asyncio.new_event_loop()

		self.max_restarts = 1
		self.restarts = 0

		self.process = Process(target=self.__run, kwargs=dict(
			environment=self,
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

	@staticmethod
	def __run(environment):
		"""
		The actual process that runs the separate controller instance.
		:param environment: EnvironmentProcess class specific for this process.
		:type environment: EnvironmentProcess
		"""
		from pyplanet.core.instance import Instance
		import logging

		logging.getLogger(__name__).info('Starting pool process for \'{}\'...'.format(environment.name))

		# Start instance.
		instance = Instance(process=environment)
		environment.loop.run_until_complete(instance.start())
		environment.loop.run_forever()
