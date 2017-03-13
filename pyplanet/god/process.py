from multiprocessing import Process


class EnvironmentProcess:

	def __init__(self, environment_name='default'):
		self.name = environment_name
		self.process = Process(target=self.__run, kwargs=dict(
			environment=self,
		))

	@staticmethod
	def __run(environment):
		print('Process for environment {}'.format(environment.name))
