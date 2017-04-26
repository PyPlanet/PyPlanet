from pyplanet.apps.config import AppConfig
from pyplanet.contrib.setting import Setting


class MigrationTestConfig(AppConfig):
	name = 'tests.apps.migration_test'

	SETTING_1 = Setting('test_setting_1', 'Setting 1')
	SETTING_2 = Setting('test_setting_2', 'Integer test', type=int, default=-1)
	SETTING_3 = Setting('test_setting_3', 'Set test', type=set, default=set())

	async def on_start(self):
		await self.context.setting.register(self.SETTING_1, self.SETTING_2, self.SETTING_3)
