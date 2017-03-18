from multiprocessing import Process
import dill

import asyncio


class EnvironmentProcess:

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
		# self.queue = queue
		self.name = environment_name
		self.loop = asyncio.new_event_loop()

		self.max_restarts = 1
		self.restarts = 0

		payload = dill.dumps((
			[],
			dict(
				environment=self,
			)
		))
		self.process = Process(target=EnvironmentProcess.__run, args=[payload])

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
	def __run(dilled_args):
		"""
		The actual process that runs the separate controller instance.
		:param dilled_args: ::::: EnvironmentProcess class specific for this process.
		:type dilled_args:  ::::: EnvironmentProcess
		"""
		args, kwargs = dill.loads(dilled_args)
		environment = kwargs['environment']

		from pyplanet.core.instance import Instance
		import logging

		logging.getLogger(__name__).info('Starting pool process for \'{}\'...'.format(environment.name))

		# Start instance.
		instance = Instance(process=environment)
		environment.loop.run_until_complete(instance.start())
		environment.loop.run_forever()
