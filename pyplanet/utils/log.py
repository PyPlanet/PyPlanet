import logging
import logging.config

from pyplanet.conf import settings


def initiate_logger():
	if settings.LOGGING_CONFIG == 'logging.config.dictConfig':
		logging.config.dictConfig(settings.LOGGING)


class RequireDebugFalse(logging.Filter):
	def filter(self, record):
		return not settings.DEBUG


class RequireDebugTrue(logging.Filter):
	def filter(self, record):
		return settings.DEBUG
