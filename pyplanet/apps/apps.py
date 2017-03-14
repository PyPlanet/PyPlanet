import threading
import importlib

from pyplanet.core.exceptions import InproperlyConfigured


class Apps:
	"""
	The apps class contains the context applications, loaded or not loaded in order of declaration or requirements
	if given by app configuration.

	The apps should contain a configuration class that could be loaded for reading out metadata, options and other
	useful information such as description, author, version and more.
	"""

	def __init__(self, apps=list()):
		"""
		Initiate registry with pre-loaded apps.
		:param apps: Pre-loaded apps.
		:type apps: list
		"""
		if not isinstance(apps, list):
			raise InproperlyConfigured('The setting APPS should contain a dictionary with pool names and array key with apps!')

		# Set the preloaded apps.
		self.apps = apps

		# Set ready states.
		self.apps_ready = self.ready = False

		# Set a lock for threading.
		self._lock = threading.Lock()

		if len(apps) > 0:
			self.populate(apps)

	def populate(self, apps):
		"""
		Loads application into the apps registry. Once you populate, the order isn't yet been decided.
		After all imports are done you should shuffle the apps list so it's in the right order of execution!
		TODO: Make sure core apps are always loaded in given order.

		:param apps: Apps list.
		:type apps: list
		"""
		if self.ready:
			return

		# Load modules.
		for module_name in apps:
			pass
