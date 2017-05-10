from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.pyplanet.dev import DevComponent
from pyplanet.apps.core.pyplanet.setting import SettingComponent
from pyplanet.apps.core.pyplanet.views.logo import LogoView


class PyPlanetConfig(AppConfig):
	core = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate components.
		self.setting = SettingComponent(self)
		self.dev = DevComponent(self)

		# Initiate logo view.
		self.logo = LogoView(manager=self.context.ui)

	async def on_init(self):
		# Call components.
		await self.setting.on_init()
		await self.dev.on_init()

	async def on_start(self):
		# Call components.
		await self.setting.on_start()
		await self.dev.on_start()

		# Display logo.
		await self.logo.display()

		# Listeners.
		self.instance.signal_manager.listen('maniaplanet:player_connect', self.on_connect)

	async def on_connect(self, player, **kwargs):
		await self.logo.display(player_logins=[player.login])
