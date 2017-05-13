from pyplanet.apps.config import AppConfig
from pyplanet.contrib.setting import Setting


class MigrationTest(AppConfig):
	SETTING_1 = Setting('test_setting_1', 'Setting 1', Setting.CAT_GENERAL)
	SETTING_2 = Setting('test_setting_2', 'Integer test', Setting.CAT_OTHER, type=int, default=-1)
	SETTING_3 = Setting('test_setting_3', 'Set test', Setting.CAT_FEATURES, type=set, default=set())
	SETTING_4 = Setting('test_setting_4', 'Enable this or that', Setting.CAT_FEATURES, type=bool, description='Large description that should break into multiple lines when displaying to the clients. Please test if this is the case at all.. Large description that should break into multiple lines when displaying to the clients. Please test if this is the case at all. Large description that should break into multiple lines when displaying to the clients. Please test if this is the case at all. Large description that should break into multiple lines when displaying to the clients. Please test if this is the case at all.')
	SETTING_5 = Setting('test_setting_5', 'Set test', Setting.CAT_FEATURES, type=set, default=set())

	async def on_start(self):
		await self.context.setting.register(
			self.SETTING_1, self.SETTING_2, self.SETTING_3, self.SETTING_4, self.SETTING_5
		)
