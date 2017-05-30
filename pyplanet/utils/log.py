import logging
import logging.config
import sys
import traceback
from pprint import pprint

from raven import Client
from logging.handlers import QueueHandler as BaseQueueHandler

from pyplanet import __version__ as version
from pyplanet.conf import settings
from pyplanet.core.exceptions import ImproperlyConfigured


IGNORED_PATHS = [
	'aiomysql',
]
IGNORED_TEXT = [
	'InternalError: Packet sequence number wrong',
	'Lost connection to',
]


class Raven:  # pragma: no cover
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


def initiate_logger():  # pragma: no cover
	if settings.LOGGING_CONFIG == 'logging.config.dictConfig':
		logging.config.dictConfig(settings.LOGGING)


def handle_exception(exception=None, module_name=None, func_name=None, extra_data=None, force=False):  # pragma: no cover
	# Test for ignored exceptions
	if exception and isinstance(exception, (ImproperlyConfigured,)):
		return

	from pyplanet.core import Controller
	if settings.DEBUG or settings.LOGGING_REPORTING == 0:
		if exception:
			logging.exception(exception)
		return

	# Filter out exceptions.
	ignore = False
	try:
		stack = traceback.extract_stack()
		for frame in stack:
			if any(ig in frame.filename for ig in IGNORED_PATHS):
				ignore = True
				break
	except:
		pass
	try:
		if not force:
			if any(ig.lower() in str(exception).lower() for ig in IGNORED_TEXT):
				ignore = True
	except:
		pass

	if ignore:
		return

	# Extra Data.
	if not extra_data:
		extra_data = dict()
	extra_data = extra_data.copy()
	if Controller.instance and Controller.instance.game:
		extra_data.update(dict(game=Controller.instance.game.__dict__))

	if exception and hasattr(exception, '__dict__'):
		extra_data['report_exception'] = exception.__dict__
	if module_name:
		extra_data['report_module_name'] = module_name
	if func_name:
		extra_data['report_func_name'] = func_name

	if settings.LOGGING_REPORTING == 3:
		extra_data['report_privacy'] = 'allow-share-contrib-apps'
	else:
		extra_data['report_privacy'] = 'deny-share-contrib-apps'

	if settings.LOGGING_REPORTING >= 2:
		Raven.get_client().extra_context(extra_data)

	# Send to sentry.
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


class QueueHandler(BaseQueueHandler):  # pragma: no cover
	def prepare(self, record):
		# Override due to bug
		self.format(record)
		record.msg = record.msg or record.message
		record.args = None
		record.exc_info = None
		return record
