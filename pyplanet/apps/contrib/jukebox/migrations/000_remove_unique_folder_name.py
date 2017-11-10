from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.mapfolder import MapFolder


def upgrade(migrator: SchemaMigrator):
	try:
		migrate(
			migrator.drop_index(MapFolder._meta.db_table, 'mapfolder_name'),
		)
	except Exception as e:
		print(str(e))
		print('Migration failed but silencing error!')


def downgrade(migrator: SchemaMigrator):
	pass
