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
				dsn='https://bcbafd2d81234d53b32c66077ae0a008:98dcc46acc484eeb95ebf9f0c30e6dd4@sentry.s3.toffe.me/2',
				environment='development' if settings.DEBUG else 'production',
				release=version,
				include_paths=['pyplanet']
			)
		return cls.CLIENT


def initiate_logger():
	if settings.LOGGING_CONFIG == 'logging.config.dictConfig':
		logging.config.dictConfig(settings.LOGGING)


def handle_exception(exception=None, module_name=None, func_name=None, extra_data=None):
	from pyplanet.core import Controller
	if settings.DEBUG:
		return

	if not extra_data:
		extra_data = dict()
	extra_data = extra_data.copy()
	if Controller.instance and Controller.instance.game:
		extra_data.update(dict(game=Controller.instance.game.__dict__))

	Raven.get_client().extra_context(extra_data)

	exc_info = sys.exc_info()
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
