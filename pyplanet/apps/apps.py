import threading
import importlib
from collections import OrderedDict

from pyplanet.apps.config import AppConfig
from pyplanet.core.exceptions import ImproperlyConfigured, InvalidAppModule


class Apps:
	"""
	The apps class contains the context applications, loaded or not loaded in order of declaration or requirements
	if given by app configuration.

	The apps should contain a configuration class that could be loaded for reading out metadata, options and other
	useful information such as description, author, version and more.
	"""

	def __init__(self):
		"""
		Initiate registry with pre-loaded apps.
		:param apps: Pre-loaded apps.
		:type apps: list
		"""
		self.apps = OrderedDict()

		# Set ready states.
		self.apps_ready = self.ready = False

		# Set a lock for threading.
		self._lock = threading.Lock()

	def populate(self, apps, in_order=False):
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
		for entry in apps:
			app = AppConfig.import_app(entry)

			# Check if the app is unique.
			if app.label in self.apps:
				raise ImproperlyConfigured('Application labels aren\'t unique! Duplicates: {}'.format(app.label))

			# Add app to list of apps.
			app.apps = self
			self.apps[app.label] = app

			print(app)
