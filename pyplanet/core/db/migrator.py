"""
The database migrator class has logic for migrating existing models and holds some information like actual versions
and differences.
"""
import peewee

from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import (
	PostgresqlMigrator, SqliteMigrator, MySQLMigrator
)

from pyplanet.core.exceptions import ImproperlyConfigured


class Migrator:
	def __init__(self, db):
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

	async def migrate(self):
		"""
		Migrate all models.
		:return:
		"""
		from .models.migration import Migration

		# Get all models that don't have a table defined yet, and create those.
		for name, (app, name, model) in self.db.registry.models.items():
			applied_migrations = list(Migration.select().where(
				(Migration.app == app.label) & (Migration.applied == True)
			))

			if not model.table_exists() and len(applied_migrations) == 0:
				model.create_table(False)
				# Fake apply all migrations for this model.
				# TODO:.

			# TODO: Look for unapplied migrations
			# TODO: Execute migrations
