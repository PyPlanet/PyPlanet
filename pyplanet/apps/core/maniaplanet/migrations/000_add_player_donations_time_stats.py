from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.player import Player


def upgrade(migrator: SchemaMigrator):
	total_playtime = IntegerField(default=0, null=False)
	total_donations = IntegerField(default=0, null=False)

	migrate(
		migrator.add_column(Player._meta.db_table, 'total_playtime', total_playtime),
		migrator.add_column(Player._meta.db_table, 'total_donations', total_donations),
	)


def downgrade(migrator: SchemaMigrator):
	migrate(
		migrator.drop_column(Player._meta.db_table, 'total_playtime'),
		migrator.drop_column(Player._meta.db_table, 'total_donations'),
	)
