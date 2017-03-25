
class ImproperlyConfigured(Exception):
	"""The configuration is not given or is invalid."""
	pass


class AppRegistryNotReady(Exception):
	"""The registry was not yet ready to invoke"""
	pass


class InvalidAppModule(Exception):
	"""The given app string is invalid or the app itself is misconfigured!"""


class TransportException(Exception):
	"""The XML-RPC tunnel got a transport error."""


class SignalException(Exception):
	"""Signal receiver thrown an exception!"""


class SignalGlueStop(Exception):
	"""Throw this exception inside of your glue method to stop executing the signal."""
