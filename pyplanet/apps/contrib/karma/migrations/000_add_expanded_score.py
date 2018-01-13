from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.karma import Karma


def upgrade(migrator: SchemaMigrator):
	expanded_score_field = FloatField(null=True)
	migrate(
		migrator.drop_not_null(Karma._meta.db_table, 'score'),
		migrator.add_column(Karma._meta.db_table, 'expanded_score', expanded_score_field),
	)


def downgrade(migrator: SchemaMigrator):
	pass
