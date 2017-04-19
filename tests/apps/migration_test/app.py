from pyplanet.apps.config import AppConfig


class MigrationTestConfig(AppConfig):
	name = 'tests.apps.migration_test'

	async def on_start(self):
		pass
