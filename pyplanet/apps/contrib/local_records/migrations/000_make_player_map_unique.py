from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.local_record import LocalRecord


def upgrade(migrator: SchemaMigrator):
	migrate(
		migrator.add_index(LocalRecord._meta.table_name, [
			'player_id', 'map_id'
		], unique=True),
	)


def downgrade(migrator: SchemaMigrator):
	pass
