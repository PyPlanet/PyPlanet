from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.pyplanet.permissions import register_permissions
from pyplanet.apps.core.pyplanet.setting import SettingComponent


class PyPlanetConfig(AppConfig):
	name = 'pyplanet.apps.core.pyplanet'
	core = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate components.
		self.setting = SettingComponent(self)

	async def on_init(self):
		# Register permissions.
		await register_permissions(self)

		# Call components.
		await self.setting.on_init()

	async def on_start(self):
		# Call components.
		await self.setting.on_start()
