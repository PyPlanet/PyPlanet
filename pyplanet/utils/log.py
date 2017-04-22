import logging
import logging.config

import sys
from raven import Client

from pyplanet import __version__ as version
from pyplanet.conf import settings


class Raven:
	CLIENT = None

	@classmethod
	def get_client(cls):
		if not cls.CLIENT:
			cls.CLIENT = Client(
				dsn='https://ca2c93716e0943debde509036d7e9c0d:c39a00a09df4411bad4ebf49780550c6@sentry.io/158911',
				environment='development' if settings.DEBUG else 'production',
				release=version,
				include_paths=['pyplanet']
			)
		return cls.CLIENT


def initiate_logger():
	if settings.LOGGING_CONFIG == 'logging.config.dictConfig':
		logging.config.dictConfig(settings.LOGGING)


def handle_exception(exception, module_name, func_name):
	from pyplanet.core import Controller
	if not settings.DEBUG:
		return

	exc_info = sys.exc_info()
	if Controller.instance and Controller.instance.game:
		Raven.get_client().extra_context(Controller.instance.game.__dict__)
	Raven.get_client().captureException(exc_info=exc_info)


class RequireDebugFalse(logging.Filter):
	def filter(self, record):
		return not settings.DEBUG


class RequireDebugTrue(logging.Filter):
	def filter(self, record):
		return settings.DEBUG


class RequireException(logging.Filter):
	def filter(self, record):
		return bool(record.exc_info)
