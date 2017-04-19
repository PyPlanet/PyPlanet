import pytest

from pyplanet.core import Controller
from pyplanet.core.db.models import migration
from tests import drop_tables


@pytest.mark.asyncio
async def test_db_migration():
	instance = Controller.prepare(name='default').instance
	await instance.db.connect()
	await instance.apps.discover()
	# await drop_tables()

	with instance.db.allow_sync():
		migration.Migration.create_table(True)
		await instance.db.migrator.migrate()

	# Reset to simulate second startup
	instance.db.migrator.pass_migrations = set()
	with instance.db.allow_sync():
		await instance.db.migrator.migrate()
	assert len(instance.db.migrator.pass_migrations) == 0
