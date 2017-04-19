from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models import TestModel

sample_field = CharField(default='unknown')


def upgrade(migrator: SchemaMigrator):
	migrate(
		migrator.add_column(TestModel._meta.db_table, 'sample', sample_field)
	)


def downgrade(migrator: SchemaMigrator):
	pass
