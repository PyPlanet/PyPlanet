
class InproperlyConfigured(Exception):
	"""The configuration is not given or is invalid."""
	pass


class AppRegistryNotReady(Exception):
	"""The registry was not yet ready to invoke"""
	pass
