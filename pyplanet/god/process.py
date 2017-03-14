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
		self.name = environment_name

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
		# print('Process for environment {}'.format(environment.name))
		# print('Having following queue: ', environment.queue.__dict__)

		time.sleep(5)
