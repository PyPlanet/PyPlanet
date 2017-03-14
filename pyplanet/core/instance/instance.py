from pyplanet.apps import Apps
from pyplanet.conf import settings
from pyplanet.core.exceptions import InproperlyConfigured


class Instance:
	def __init__(self, process):
		"""
		The actual instance of the controller.
		:param process: EnvironmentProcess class specific for this process.
		:type process: pyplanet.god.process.EnvironmentProcess
		"""
		self.process = process
		self.apps = Apps()

		# Populate apps.
		try:
			self.apps.populate(settings.MANDATORY_APPS + settings.APPS[self.process.pool_name])
		except KeyError as e:
			raise InproperlyConfigured(
				'One of the pool names doesn\'t reflect intot the APPS setting! You must '
				'declare the apps per pool! ({})'.format(str(e))
			)
