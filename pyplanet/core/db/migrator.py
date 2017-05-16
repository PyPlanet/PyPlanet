"""
The database migrator class has logic for migrating existing models and holds some information like actual versions
and differences.
"""
import asyncio

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
		creating = list()
		for name, (app, name, model) in self.db.registry.models.items():
			if not model.table_exists():
				creating.append(model)
				self.pass_migrations.add(app.label)

		self.db.engine.create_tables(creating, safe=True)

	async def check(self):
		"""
		Check the database health.
		"""
		try:
			if isinstance(self.migrator, MySQLMigrator):
				cursor = self.db.engine.execute_sql(
					'SELECT DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME LIKE %s;',
					self.db.engine.database
				)
				result = cursor.fetchone()
				if len(result) == 1:
					if result[0] != 'utf8mb4_unicode_ci':
						logger.error(
							'Your database collate is \'{}\' and it should be \'utf8mb4_unicode_ci\'! '
							'Please change your database collate right now!'.format(result[0])
						)
						logger.warning(
							'Change with: '
							'ALTER SCHEMA {} DEFAULT CHARACTER SET utf8mb4  DEFAULT COLLATE utf8mb4_unicode_ci ;'.format(
								self.db.engine.database
							)
						)
						logger.info('Wait 5 seconds to ignore!... (We strongly advice to change it!)')
						await asyncio.sleep(5)
		except:
			pass  # Totally ignore.

	async def migrate(self):
		"""
		Migrate all models.
		
		:return:
		"""
		from .models.migration import Migration

		# Create tables + skip migrations.
		await self.create_tables()

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

				# Log message.
				logger.info('Successfully executed migration: {}'.format(name))

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
