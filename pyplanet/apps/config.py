import importlib
import os

from pyplanet.core.exceptions import ImproperlyConfigured, InvalidAppModule


class AppConfig:
	"""
	This class is the base class for the Applications metadata class. The class holds information and hooks
	that will be executed after initiation for example.
	"""
	name = None
	lable = None
	human_name = None
	path = None

	def __init__(self, app_name, app_module):
		# The full python module path. The postfix `*.app.*Config` is always the same!
		# Example: pyplanet.contrib.apps.games.trackmania.app.TrackmaniaConfig
		self.name = app_name

		# The apps root module.
		# Example: pyplanet.contrib.apps.games.trackmania
		self.module = app_module

		# The apps registry will be injected into the app config.
		self.apps = None

		# Make sure we give the core attribute the default value of false. This indicates if it's an internally
		# module.
		self.core = getattr(self, 'core', False)

		# The label can be given by the module, or automatically determinated on the last component.
		if not hasattr(self, 'label') or getattr(self, 'label', None) is None:
			self.label = app_name.rpartition(".")[2]

			# If the module is a core contrib module, we give the label a prefix (contrib.app).
			if self.core is True:
				self.label = 'core.{}'.format(self.label)

		# Human-readable name for the application eg. `MyApp`.
		if not hasattr(self, 'human_name') or getattr(self, 'human_name', None) is None:
			self.human_name = self.label.title()

		# Filesystem path to the application directory eg.
		if not hasattr(self, 'path') or getattr(self, 'path') is None:
			self.path = self._path_from_module(app_module)

	def __repr__(self):
		return '<%s: %s>' % (self.__class__.__name__, self.label)

	def on_ready(self):
		pass

	def _path_from_module(self, module):
		"""Attempt to determine app's filesystem path from its module."""
		paths = list(getattr(module, '__path__', []))

		if len(paths) != 1:
			filename = getattr(module, '__file__', None)
			if filename is not None:
				paths = [os.path.dirname(filename)]
			else:
				# Can be bugged for unknown reasons.
				paths = list(set(paths))

		if len(paths) > 1:
			raise ImproperlyConfigured(
				'The app module {} has multiple filesystem locations {}; '
				'you must configure this app with an AppConfig subclass '
				'with a \'path\' class attribute.'.format(module, paths))

		elif not paths:
			raise ImproperlyConfigured(
				'The app module {} has no filesystem location, '
				'you must configure this app with an AppConfig subclass '
				'with a \'path\' class attribute.'.format(module))

		return paths[0]

	@staticmethod
	def import_app(entry):
		# Import the module, we need to strip down the path into namespace, file and class.
		module_path, _, cls_name = entry.rpartition('.')
		if not module_path:
			raise ImproperlyConfigured('Module for your app {} can\'t be found!'.format(entry))

		# Try to load the app module, containing the class.
		try:
			module = importlib.import_module(module_path)
			module = getattr(module, cls_name)
		except ImportError:
			raise ImproperlyConfigured(
				'Can\'t load the app {}. Can\'t find the app config!'.format(entry)
			)
		except AttributeError:
			raise ImproperlyConfigured(
				'Can\'t load the app {}. Can\'t load the app class!'.format(entry)
			)

		# Last check if subclass of appconfig.
		if not issubclass(module, AppConfig):
			raise InvalidAppModule('Your required app {} couldn\'t be loaded!'.format(entry))

		# Get name and other attributes.
		try:
			app_name = module.name
			if app_name is None:
				raise AttributeError()
		except AttributeError:
			raise ImproperlyConfigured(
				'App {} must supply a name attribute.'.format(entry)
			)

		# Ensure app_name points to a valid module.
		try:
			app_module = importlib.import_module(app_name)
		except ImportError:
			raise ImproperlyConfigured(
				'Can\'t import {}. Check that \'{}.{}.name\' is correct.'.format(
					app_name, module_path, cls_name
				)
			)

		return module(app_name, app_module)
