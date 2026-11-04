import asynctest
from playhouse.reflection import Introspector

from pyplanet.core.db.models import migration

from tests.base import TestCase


class TestConnection(TestCase):
	async def test_connection(self):
		instance = self.instance
		await instance.db.connect()
		with instance.db.allow_sync():
			introspector = Introspector.from_database(instance.db.engine)
			db_name = introspector.get_database_name()
			assert db_name and len(db_name) > 0


class TestModelDiscovery(TestCase):
	async def test_discovery(self):
		instance = self.instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

		assert len(instance.db.registry.models.keys()) > 0
		assert len(instance.db.registry.app_models.keys()) > 0


class TestModelTableCreation(TestCase):
	async def test_creation(self):
		instance = self.instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

		with instance.db.allow_sync():
			introspector = Introspector.from_database(instance.db.engine)
			metadata = introspector.introspect()
			assert len(metadata.model_names) > 0


class TestMigrations(TestCase):
	async def test_db_migration(self):
		instance = self.instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

		with instance.db.allow_sync():
			migration.Migration.create_table(True)
			await instance.db.migrator.migrate()

		# Reset to simulate second startup
		instance.db.migrator.pass_migrations = set()
		with instance.db.allow_sync():
			await instance.db.migrator.migrate()
		assert len(instance.db.migrator.pass_migrations) == 0
