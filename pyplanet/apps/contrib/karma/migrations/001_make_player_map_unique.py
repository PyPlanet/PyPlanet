import logging
from peewee import *
from playhouse.migrate import migrate, SchemaMigrator

from ..models.karma import Karma

logger = logging.getLogger(__name__)


def upgrade(migrator: SchemaMigrator):
	# Fix the duplicates in the current setup.
	total_processed = 0
	results = None
	while results is None or len(results) > 0:
		results = (Karma.select()
				   .order_by(Karma.created_at.desc())
				   .group_by(Karma.player_id, Karma.map_id)
				   .having(fn.Count(Karma.player_id) > 1))

		for result in results:
			result.delete_instance()
			total_processed += 1

	logger.warning('Removing duplicated karma votes, processed {} rows! Now going to execute the migration...'.format(
		total_processed
	))

	# Create the indexes.
	migrate(
		migrator.add_index(Karma._meta.db_table, [
			'player_id', 'map_id'
		], unique=True),
	)


def downgrade(migrator: SchemaMigrator):
	pass
