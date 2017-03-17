import threading
import importlib
from collections import OrderedDict

import logging

from pyplanet.apps.config import AppConfig
from pyplanet.core.exceptions import ImproperlyConfigured, InvalidAppModule
from pyplanet.god.thread import AppThread


class Apps:
	"""
	The apps class contains the context applications, loaded or not loaded in order of declaration or requirements
	if given by app configuration.

	The apps should contain a configuration class that could be loaded for reading out metadata, options and other
	useful information such as description, author, version and more.
	"""

	def __init__(self, instance):
		"""
		Initiate registry with pre-loaded apps.
		:param instance: Instance of the controller.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance

		self.apps = OrderedDict()

		# Set ready states.
		self.apps_ready = self.ready = False

		# Set a lock for threading.
		self._lock = threading.Lock()

	def populate(self, apps, in_order=False):
		"""
		Loads application into the apps registry. Once you populate, the order isn't yet been decided.
		After all imports are done you should shuffle the apps list so it's in the right order of execution!

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

	def shuffle(self):
		# TODO
		self.ready = True
		pass

	def discover(self):
		"""
		The discover function will discover all models from apps in the right order and register it to the
		:return:
		"""
		for label, app in self.apps.items():
			self.instance.db.registry.init_app(app)

	def start(self):
		if self.apps_ready:
			raise Exception('Apps are not yet ordered!')

		# TODO: Fetch all apps logic.
		# TODO: Register models some kind of shit.

		# The apps are in order, lets loop over them.
		for label, app in self.apps.items():
			logging.debug('App is ready: {}'.format(label))
			app.on_ready()

		logging.info('Apps successfully started!')
