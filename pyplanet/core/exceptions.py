
class ImproperlyConfigured(Exception):
	"""The configuration is not given or is invalid."""
	pass


class AppRegistryNotReady(Exception):
	"""The registry was not yet ready to invoke"""
	pass


class InvalidAppModule(Exception):
	"""The given app string is invalid or the app itself is misconfigured!"""
