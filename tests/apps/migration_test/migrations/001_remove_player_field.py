from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models import TestModel


def upgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(TestModel._meta.db_table, 'player_id')
	)


def downgrade(migrator: SchemaMigrator):
	pass
