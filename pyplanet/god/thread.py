import threading

import logging
from time import sleep


class AppThread(threading.Thread):

	@staticmethod
	def create(app, **kwargs):
		"""
		Create a new thread for the specific app and instance.
		:param app: Application Configuration instance.
		:param instance: Controller Instance.
		:type app: pyplanet.apps.AppConfig
		:type instance: pyplanet.core.instance.Instance
		:return: the new thread, prepared to start.
		:rtype: AppThread
		"""
		kwargs.update(dict(app=app))
		return AppThread(name='AppThread-{}'.format(app.label), kwargs=kwargs)

	def run(self):
		"""
		Run the app in the specific app thread.
		:return:
		"""
		logger = logging.getLogger(__name__)
		logger.debug('Starting thread for app \'{}\''.format(self._kwargs['app'].name))
		sleep(50)
		pass
