import threading
import logging

from collections import OrderedDict

from pyplanet.utils.toposort import toposort
from pyplanet.apps.config import AppConfig
from pyplanet.core.exceptions import ImproperlyConfigured


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

		# Listen to events
		self.instance.signal_manager.listen('contrib.mode:script_mode_changed', self._on_mode_change)

	def populate(self, apps, in_order=False):
		"""
		Loads application into the apps registry. Once you populate, the order isn't yet been decided.
		After all imports are done you should shuffle the apps list so it's in the right order of execution!

		:param apps: Apps list.
		:param in_order: Is the list already in order?
		:type apps: list
		"""
		if self.ready:
			return

		populated_apps = dict()
		dep_dict = dict()

		# Load modules.
		for entry in apps:
			app = AppConfig.import_app(entry, self.instance)

			# Check if the app is unique.
			if app.label in self.apps:
				raise ImproperlyConfigured('Application labels aren\'t unique! Duplicates: {}'.format(app.label))

			# Inject apps instance into app itself.
			app.apps = self

			# Get dependencies to other apps.
			deps = getattr(app, 'app_dependencies', list())
			if not type(deps) is list:
				deps = list()

			# Add to the list so it can get ordered by dependencies. (not if in_order is true).
			if in_order:
				self.apps[app.label] = app
			else:
				populated_apps[app.label] = app

				# Add nodes of dependencies.
				dep_dict[app.label] = deps

		if in_order:
			return

		# Determinate order.
		order = toposort(dep_dict)

		# Add in order
		for label in order:
			try:
				self.apps[label] = populated_apps[label]
			except KeyError:
				if label.startswith('core.'):
					pass
				else:
					raise Exception('One of the apps depends on a non existing app: {}'.format(label))

	async def check(self):
		"""
		Check and remove unsupported apps based on the current game and script mode. 
		"""
		apps_dict = OrderedDict()
		for label, app in self.apps.items():
			if not app.is_game_supported('trackmania' if self.instance.game.game == 'tm' else 'shootmania'):
				logging.info('Unloading app {}. Doesn\'t support the current game!'.format(label))
				await app.on_stop()
				await app.on_destroy()
				del app

			elif not app.is_mode_supported(await self.instance.mode_manager.get_current_script()):
				logging.info('Unloading app {}. Doesn\'t support the current script mode!'.format(label))
				await app.on_stop()
				await app.on_destroy()
				del app

			else:
				apps_dict[label] = app

		self.apps = apps_dict

	async def discover(self):
		"""
		The discover function will discover all models, signals and more
		from apps in the right order.
		"""
		for label, app in self.apps.items():
			# Discover models.
			self.instance.db.registry.init_app(app)

			# Discover signals.
			self.instance.signal_manager.init_app(app)

		# Finishing signal manager.
		self.instance.signal_manager.finish_reservations()

	async def init(self):
		if self.apps_ready:
			raise Exception('Apps are not yet ordered!')
		for label, app in self.apps.items():
			await app.on_init()

	async def start(self):
		if self.apps_ready:
			raise Exception('Apps are not yet ordered!')

		# The apps are in order, lets loop over them.
		for label, app in self.apps.items():
			await app.on_start()
			logging.debug('App is ready: {}'.format(label))
		logging.info('Apps successfully started!')

	async def _on_mode_change(self, unloaded_script, loaded_script, **kwargs):
		await self.check()
