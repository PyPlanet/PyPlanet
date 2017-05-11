"""
The database registry class is used for managing apps models and states related to the Peewee backed ORM.
"""
import os
import inspect
import importlib

from glob import glob


def get_app_models(app):
	from .model import Model
	try:
		models_module = importlib.import_module('{}.models'.format(app.name))
		for name, obj in inspect.getmembers(models_module):
			if inspect.isclass(obj) and issubclass(obj, Model):
				if obj.__name__ == 'TimedModel':
					continue
				yield name, obj
	except Exception as e:
		return list()


def get_app_migrations(app):
	try:
		migration_files = glob(os.path.join(app.path, 'migrations', '*.py'))
		migration_files.sort()

		for file in migration_files:
			dir, file_name = os.path.split(file)
			name, ext = file_name.split('.')
			yield file, dir, name, ext
	except:
		return list()


class Registry:
	def __init__(self, instance, db):
		self.instance = instance
		self.db = db

		# Cache app contexts
		self.app_configs = dict()
		self.app_models = dict()
		self.app_migrations = dict()

		# Models are saved as [app_label.model_classname] = (app, name, model)
		self.models = dict()

	def init_app(self, app):
		"""
		Initiate the app database assets.
		:param app: App instance
		:type app: pyplanet.apps.AppConfig
		"""
		# Determinate correct paths.
		root_path = app.path
		models_path = os.path.join(root_path, 'models') \
			if os.path.exists(os.path.join(root_path, 'models')) and os.path.isdir(os.path.join(root_path, 'models')) \
			else root_path
		migrations_path = os.path.join(root_path, 'migrations')

		# Set paths in the config context.
		if os.path.exists(models_path):
			if not os.path.exists(migrations_path):
				try:
					os.mkdir(migrations_path)
				except:
					pass

		# Import the model module.
		self.app_models[app.label] = models = list(get_app_models(app))
		for name, model in models:
			self.models['{}.{}'.format(app.label, name)] = app, name, model

		# Import migration files.
		self.app_migrations[app.label] = migrations = list(get_app_migrations(app))
