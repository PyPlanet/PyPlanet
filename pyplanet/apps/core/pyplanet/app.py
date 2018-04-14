import asyncio
import logging
import platform

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.pyplanet.dev import DevComponent
from pyplanet.apps.core.pyplanet.setting import SettingComponent
from pyplanet.apps.core.pyplanet.views.controller import ControllerView
from pyplanet.conf import settings
from pyplanet.contrib.command import Command

from pyplanet import __version__ as version
from pyplanet.utils import semver
from pyplanet.utils.pip import Pip
from pyplanet.utils.releases import UpdateChecker
from pyplanet.views.generics import ask_confirmation


class PyPlanetConfig(AppConfig):
	core = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate components.
		self.setting = SettingComponent(self)
		self.dev = DevComponent(self)

		# Initiate app (global) view.
		self.controller_view = ControllerView(manager=self.context.ui)

		# Status.
		self.in_progress = False

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
		await self.controller_view.display()

		# Listeners.
		self.context.signals.listen('maniaplanet:player_connect', self.on_connect)
		await self.instance.command_manager.register(
			Command('version', self.chat_version),
			Command('upgrade', self.chat_upgrade, admin=True, description='Upgrade PyPlanet installation (Experimental)')
				.add_param('to_version', type=str, default=None, required=False, help='Upgrade to specific version')
		)

	async def on_connect(self, player, **kwargs):
		await self.controller_view.display(player_logins=[player.login])

	async def chat_version(self, player, *args, **kwargs):
		message = '$ff0PyPlanet: $fff{}$ff0 (Python $fff{}$ff0), current apps: $fff'.format(version, platform.python_version())
		message += '$ff0, $fff'.join(self.instance.apps.apps.keys())
		await self.instance.chat(message, player)

	async def chat_upgrade(self, player, data, *args, **kwargs):
		package = 'pyplanet'
		to_version = data.to_version
		if player.level != 3:
			return await self.instance.chat('$f00Only MasterAdmin can upgrade installation!', player)
		if not settings.SELF_UPGRADE:
			return await self.instance.chat('$f00In-game upgrade method is disabled by the hoster!', player)

		# Getting PIP.
		pip = Pip()
		await self.instance.gbx.multicall(
			self.instance.chat('$09fPIP:$fff pip-command: {}'.format(pip.command), player),
			self.instance.chat('$09fPIP:$fff pip-status: {}'.format(
				'PIP is ready and supported' if pip.is_supported else '$f00Unsupported! Use manual method!'
			), player)
		)
		if not pip.is_supported:
			return

		# Validate new version
		if to_version:
			if to_version not in UpdateChecker.releases:
				return await self.instance.chat(
					'$f00The version \'{}\' is not known to be a PyPlanet version!'.format(to_version), player
				)
		else:
			to_version = UpdateChecker.latest

		# Check if to_version is actual newer.
		from pyplanet import __version__ as current_version
		if semver.compare(to_version, current_version) < 0:
			return await self.instance.chat(
				'$f00Downgrading is not possible with the in-game upgrade method!'.format(to_version), player
			)

		# Ask the user, give warnings.
		cancel = bool(await ask_confirmation(
			player,
			'Are you sure you want to upgrade PyPlanet from \'{}\' to \'{}\'?'
			'\n$f00$o$wWARNING:$g$n This method is experimental, you can break your installation! '
			'We advice to use the PIP method over the in-game upgrade method! Please '
			'be careful with big release updates!'.format(current_version, to_version),
			size='md',
		))

		if cancel:
			return

		# Execute the upgrade.
		await self.instance.gbx.multicall(
			self.instance.chat('$09fUpgrade$fff: PyPlanet is about to upgrade to {}'.format(to_version)),
			self.instance.chat('$09fUpgrade$fff: Please wait, installing new version with $09fpip$fff...'.format(to_version))
		)

		self.in_progress = True
		asyncio.ensure_future(self.send_updates())
		await asyncio.sleep(2)

		if settings.DEBUG:
			logging.getLogger(__name__).warning('DEBUG MODE, NOT ACTUALLY UPGRADING PYPLANET!!!!!!!!!!!!!!!!!!!')
			package = 'example'
			to_version = None

		statuscode, stdout, stderr = pip.install(package, target_version=to_version)

		self.in_progress = False
		await self.instance.chat('.', raw=True)

		if statuscode != 0:
			return await self.instance.gbx.multicall(
				self.instance.chat(
					'$09fUpgrade$fff: Upgrade failed! Please look at the logfiles or the following lines for information'
				),
				self.instance.chat(
					'$09fUpgrade$fff: PIP (truncated): $n{}'.format(stderr.decode()[-100:])
				),
				self.instance.chat(
					'$09fUpgrade$fff: Please use the manual PIP method for upgrading and check if your installation isn\'t broken'
				)
			)

		# Send successful message.
		await self.instance.chat(
			'$09fUpgrade$fff: PIP installation of PyPlanet succeeded! Please wait...'
		)

		# Reboot PyPlanet
		await self.instance.chat(
			'$09fUpgrade$fff: Restarting PyPlanet...'
		),
		exit(50)

	async def send_updates(self):
		await self.instance.chat(
			'$09fUpgrade$fff: $'
		)
		while self.in_progress:
			await self.instance.chat(
				'.$',
				raw=True
			)
			await asyncio.sleep(0.05)
