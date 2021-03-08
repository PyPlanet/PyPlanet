import asyncio
import logging
import platform

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.pyplanet.dev import DevComponent
from pyplanet.apps.core.pyplanet.setting import SettingComponent
from pyplanet.apps.core.pyplanet.toolbar import ToolbarComponent
from pyplanet.apps.core.pyplanet.views.command import CommandsListView
from pyplanet.apps.core.pyplanet.views.controller import ControllerView
from pyplanet.conf import settings
from pyplanet.contrib.command import Command

from pyplanet import __version__ as version
from pyplanet.utils import semver
from pyplanet.utils.functional import batch
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
		self.toolbar = ToolbarComponent(self)

		# Initiate app (global) view.
		self.controller_view = ControllerView(manager=self.context.ui)

		# Status.
		self.in_progress = False

	async def on_init(self):
		# Call components.
		await self.setting.on_init()
		await self.dev.on_init()
		await self.toolbar.on_init()

	async def on_start(self):
		# Call components.
		await self.setting.on_start()
		await self.dev.on_start()
		await self.toolbar.on_start()

		# Change some ui elements positions and visibility.
		if self.instance.game.game in ['tm', 'sm']:
			self.instance.ui_manager.properties.set_visibility('live_info', False)
			self.instance.ui_manager.properties.set_attribute('live_info', 'pos', '-125. 84. 5.')
			self.instance.ui_manager.properties.set_attribute('warmup', 'pos', '86., 87., 5.')
		else:
			self.instance.ui_manager.properties.set_visibility('Race_Checkpoint', False)
			self.instance.ui_manager.properties.set_visibility('Race_RespawnHelper', False)
			self.instance.ui_manager.properties.set_attribute('Race_BestRaceViewer', 'position', [135, -30])
			self.instance.ui_manager.properties.set_attribute('Race_Countdown', 'position', [155, -15])
			self.instance.ui_manager.properties.set_attribute('Race_LapsCounter', 'position', [155.7, -77])
			self.instance.ui_manager.properties.set_attribute('Race_LapsCounter', 'scale', 0.7)
			self.instance.ui_manager.properties.set_attribute('Race_TimeGap', 'position', [44, -45])
			self.instance.ui_manager.properties.set_attribute('Rounds_SmallScoresTable', 'position', [-160, 8])
			self.instance.ui_manager.properties.set_attribute('Race_WarmUp', 'position', [155.7, -65])
			self.instance.ui_manager.properties.set_attribute('Race_WarmUp', 'scale', 0.7)
			self.instance.ui_manager.properties.set_attribute('Race_ScoresTable', 'scale', 0.9)
			self.instance.ui_manager.properties.set_attribute('Race_SpectatorBase_Commands', 'position', [50, -87])
			await self.instance.ui_manager.properties.send_properties()

		# Display logo.
		await self.controller_view.display()

		# Listeners.
		self.context.signals.listen('maniaplanet:player_connect', self.on_connect)
		await self.instance.command_manager.register(
			Command('version', self.chat_version,
					description='Displays the current server and PyPlanet versions and the active PyPlanet plugins.'),
			Command('upgrade', self.chat_upgrade, admin=True, description='Upgrade PyPlanet installation (Experimental)')
				.add_param('to_version', type=str, default=None, required=False, help='Upgrade to specific version'),

			Command('help', target=self.chat_help, description='Shows a chat-based list with all available commands.')
				.add_param('command', nargs='*', required=False),
			Command('help', target=self.chat_help, admin=True, description='Shows a chat-based list with all available admin commands.')
				.add_param('command', nargs='*', required=False),
			Command('helpall', target=self.chat_helpall, description='Shows all available commands in a list window.'),
			Command('helpall', target=self.chat_helpall, admin=True, description='Shows all available admin commands in a list window.')
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

	async def chat_helpall(self, player, data, raw, command):
		return

	async def chat_help(self, player, data, raw, command):
		# Show usage of a single command, given as second or more params.
		if data.command:
			is_admin = bool(command.admin)
			cmd_args = data.command

			# HACK: Add / before an admin command to match the right command.
			if is_admin and cmd_args:
				cmd_args[0] = '/{}'.format(cmd_args[0])

			cmd = await self.instance.command_manager.get_command_by_command_text(cmd_args)
			if cmd:
				await self.instance.chat(
					'$z$s{}'.format(cmd.usage_text),
					player
				)
			else:
				await self.instance.chat('Command help not found', player)
			return

		# All commands.
		commands = await self.instance.command_manager.help_entries(player, command.admin)

		# Prepare and send the calls.
		calls = list()
		for cmds in batch(commands, 7):
			help_texts = [str(c) for c in cmds]
			calls.append(
				self.instance.chat(
					'$z$s{}'.format(' | '.join(help_texts)),
					player.login
				)
			)

		await self.instance.gbx.multicall(
			self.instance.chat(
				'$z$sCommand list. Help per command: /{}help [command]'.format('/' if command.admin else ''),
				player.login
			),
			*calls
		)

	async def chat_helpall(self, player, data, raw, command):
		window = CommandsListView(self, player, command.admin)
		await window.display(player=player)
		return
