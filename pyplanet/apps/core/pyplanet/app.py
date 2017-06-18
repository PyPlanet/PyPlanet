import platform

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.pyplanet.dev import DevComponent
from pyplanet.apps.core.pyplanet.setting import SettingComponent
from pyplanet.apps.core.pyplanet.views.logo import LogoView
from pyplanet.contrib.command import Command

from pyplanet import __version__ as version


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

		# Change some ui elements positions and visibility.
		self.instance.ui_manager.properties.set_visibility('live_info', False)
		self.instance.ui_manager.properties.set_attribute('live_info', 'pos', '-125. 84. 5.')
		self.instance.ui_manager.properties.set_attribute('warmup', 'pos', '86., 87., 5.')

		# Display logo.
		await self.logo.display()

		# Listeners.
		self.instance.signal_manager.listen('maniaplanet:player_connect', self.on_connect)
		await self.instance.command_manager.register(Command('version', self.chat_version))

	async def on_connect(self, player, **kwargs):
		await self.logo.display(player_logins=[player.login])

	async def chat_version(self, player, *args, **kwargs):
		message = '$ff0PyPlanet: $fff{}$ff0 (Python $fff{}$ff0), current apps: $fff'.format(version, platform.python_version())
		message += '$ff0, $fff'.join(self.instance.apps.apps.keys())
		await self.instance.chat(message, player)
