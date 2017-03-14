import time

from multiprocessing import Process


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
		self.pool_name = environment_name

		self.process = Process(target=self.__run, kwargs=dict(
			environment=self,
		))

	@staticmethod
	def __run(environment):
		"""
		The actual process that runs the separate controller instance.
		:param environment: EnvironmentProcess class specific for this process.
		:type environment: EnvironmentProcess
		"""
		from pyplanet.core.instance import Instance
		import logging
		logging.getLogger(__name__).info('Starting pool process for \'{}\'...'.format(environment.pool_name))

		# Start instance.
		instance = Instance(process=environment)
