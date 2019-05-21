from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from pyplanet.apps.core.maniaplanet.models import Map


def upgrade(migrator: SchemaMigrator):
	mx_id = IntegerField(default=None, null=True, index=True)

	migrate(
		migrator.add_column(Map._meta.db_table, 'mx_id', mx_id),
	)


def downgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(Map._meta.db_table, 'mx_id'),
	)
