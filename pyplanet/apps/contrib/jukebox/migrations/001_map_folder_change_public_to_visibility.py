from peewee import RawQuery
from playhouse.migrate import migrate, SchemaMigrator

from ..models.mapfolder import MapFolder


def upgrade(migrator: SchemaMigrator):
	try:
		query = RawQuery(MapFolder, """SELECT * FROM `mapfolder` WHERE public = 1""")
		public_folders = query.execute()

		migrate(
			migrator.add_column(MapFolder._meta.db_table, 'visibility', MapFolder.visibility),
			migrator.drop_column(MapFolder._meta.db_table, 'public')
		)

		MapFolder.update(visibility='public').where(MapFolder.id << [f.id for f in public_folders]).execute()
	except Exception as e:
		print(str(e))
		print('Migration failed but silencing error!')

def downgrade(migrator: SchemaMigrator):
	pass
