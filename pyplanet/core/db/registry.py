"""
The database registry class is used for managing apps models and states related to the Peewee backed ORM.
"""
import os


class Registry:
	def __init__(self, db):
		self.db = db

		# Cache app contexts
		self.app_configs = dict()
		self.app_models = dict()

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
		migrations_path = os.path.join(models_path, 'migrations')

		# Set paths in the config context.
		if os.path.exists(models_path):
			if not os.path.exists(migrations_path):
				os.mkdir(migrations_path)
