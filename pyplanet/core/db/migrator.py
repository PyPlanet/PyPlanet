"""
The database migrator class has logic for migrating existing models and holds some information like actual versions
and differences.
"""
import importlib

import logging
import peewee

from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import (
	PostgresqlMigrator, SqliteMigrator, MySQLMigrator
)

from pyplanet.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class Migrator:
	def __init__(self, instance, db):
		"""
		Initiate migrator.
		:param instance: Instance of controller
		:param db: Database instance.
		:type instance: pyplanet.core.instance.Instance
		:type db: pyplanet.core.db.database.Database
		"""
		self.instance = instance
		self.db = db
		self.migrator = self.__get_migrator()

		self.pass_migrations = set()

	def __get_migrator(self):
		if isinstance(self.db.engine, peewee.SqliteDatabase) or isinstance(self.db.engine, SqliteExtDatabase):
			return SqliteMigrator(self.db.engine)
		elif isinstance(self.db.engine, peewee.MySQLDatabase):
			return MySQLMigrator(self.db.engine)
		elif isinstance(self.db.engine, peewee.PostgresqlDatabase):
			return PostgresqlMigrator(self.db.engine)
		raise ImproperlyConfigured('Database engine doesn\'t support Migrations!')

	async def create_tables(self):
		for name, (app, name, model) in self.db.registry.models.items():
			if not model.table_exists():
				try:
					model.create_table(False)
					# Pass all migrations for this app.
					self.pass_migrations.add(app.label)
				except:
					raise

	async def migrate(self):
		"""
		Migrate all models.
		:return:
		"""
		from .models.migration import Migration

		# Get all models that don't have a table defined yet, and create those.
		restart = 0
		restart_exception = None
		while restart < 20:
			try:
				# HACK: Shuffle model list and try again if it fails.
				self.db.registry.models = self.db.registry.models.copy()
				await self.create_tables()
				restart = 99
			except Exception as e:
				restart_exception = e
				restart += 1
		if restart != 99:
			if restart_exception:
				raise restart_exception
			raise Exception('Can\'t create tables!')

		# Look for app migrations that are not yet applied.
		for app, migration_files in self.db.registry.app_migrations.items():
			if not migration_files:
				continue

			# Get module path + current applied migrations.
			app_module = self.instance.apps.apps[app].module.__name__
			applied_migrations = [p.name for p in Migration.select().where(
				(Migration.app == app) & (Migration.applied == True)
			)]

			# For each migration file.
			for full_path, folder, name, ext in migration_files:
				if name in applied_migrations:
					continue
				if app in self.pass_migrations:
					# Fake the migration, we just created all the models for this app. Initial setup.
					Migration.create(
						app=app,
						name=name,
						applied=True
					)
					continue

				# Apply migration..
				self.run_migration(name, app, app_module)

	def run_migration(self, name, app_label, app_module, save_migration=True):
		"""
		Run + apply migration to the actual database.
		:param name: Name of migration.
		:param app_label: App label.
		:param app_module: App module path.
		:param save_migration: Save migration state?
		"""
		from .models.migration import Migration
		mod = importlib.import_module('{}.migrations.{}'.format(app_module, name))

		try:
			with self.db.allow_sync():
				mod.upgrade(self.migrator)

				if save_migration:
					Migration.create(
						app=app_label,
						name=name,
						applied=True
					)
		except Exception as e:
			logger.warning('Can\'t migrate {}.migrations.{}: {}'.format(app_module, name, str(e)))
			raise
