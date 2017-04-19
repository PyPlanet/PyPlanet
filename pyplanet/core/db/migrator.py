"""
The database migrator class has logic for migrating existing models and holds some information like actual versions
and differences.
"""
import peewee

from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import (
	PostgresqlMigrator, SqliteMigrator, MySQLMigrator
)
from playhouse.migrate import migrate

from pyplanet.core.exceptions import ImproperlyConfigured


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

	# Create migrations model.
	# self.Migrations.create_table(fail_silently=True)

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
					# TODO: Pass migrations
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
			applied_migrations = list(Migration.select().where(
				(Migration.app == app) & (Migration.applied == True)
			))
			print(app, migration_files, applied_migrations)
		# exit()

			# TODO: Look for unapplied migrations
			# TODO: Execute migrations
