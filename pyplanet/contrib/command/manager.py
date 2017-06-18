import textwrap

from pyplanet.contrib import CoreContrib
from pyplanet.contrib.command.command import Command
from pyplanet.utils.functional import batch


class CommandManager(CoreContrib):
	"""
	The Command Manager contributed extension is a manager that controls all chat-commands in the game.
	Your app needs to use this manager to register any custom commands you want to provide.

	You should access this class within your app like this:

	.. code-block:: python

		self.instance.command_manager

	You can register your commands like this:

	.. code-block:: python

		await self.instance.command_manager.register(
			Command(command='reboot', target=self.reboot_pool, perms='admin:reboot', admin=True),
		)

	More information of the command and the options of it, see the :class:`pyplanet.contrib.command.Command` class.

	.. warning::

		Don't initiate this class yourself. Access this class from the ``self.instance.command_manager`` instance.

	"""

	def __init__(self, instance):
		"""
		Init manager.

		:param instance: Controller Instance
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		self._commands = list()

	async def on_start(self, **kwargs):
		# Register events.
		self._instance.signal_manager.listen('maniaplanet:player_chat', self._on_chat)

		# Register /help and //help
		await self.register(
			Command('help', target=self._help).add_param('command', nargs='*', required=False),
			Command('help', target=self._help, admin=True).add_param('command', nargs='*', required=False),
		)

	async def register(self, *commands):
		"""
		Register your command.

		:param commands: Command instance.
		:type commands: pyplanet.contrib.command.command.Command
		"""
		self._commands.extend(commands)

	async def _on_chat(self, player, text, cmd, **kwargs):
		# Only take action if the chat entry is a command.
		if not cmd:
			return

		# Parse command.
		argv = text.split(' ')
		if not argv:
			return

		# Replace the / in the first part.
		argv[0] = argv[0][1:]

		# Check if we need to ignore the command.
		if len(argv) > 0 and argv[0] in ['serverlogin']:
			return

		# Try to match the command prefix by one of the registered commands.
		command = None
		for cmd in self._commands:
			if cmd.match(argv):
				command = cmd
				break

		# Let the command handle the logic it needs.
		if command:
			return await command.handle(self._instance, player, argv)
		# Send command not found message.
		await self._instance.chat(
			'$z$sCommand unknown. For all commands type /help or //help. '
			'Powered by $l[http://pypla.net]$FD4Py$369Planet',
			player.login
		),

	async def _help(self, player, data, raw, command):  # pragma: no cover
		help_command = command
		filter_admin = bool(help_command.admin)

		# Show usage of a single command, given as second or more params.
		if data.command:
			cmd_args = data.command

			# HACK: Add / before an admin command to match the right command.
			if filter_admin and cmd_args:
				cmd_args[0] = '/{}'.format(cmd_args[0])

			# Find the right command.
			cmd_instance = None
			for cmd in self._commands:
				if cmd.match(cmd_args):
					cmd_instance = cmd
					break
			# If found, show the usage of the command.
			if cmd_instance:
				await self._instance.chat(
					'$z$s{}'.format(cmd_instance.usage_text),
					player
				)
				return

		# All commands.
		commands = [c for c in self._commands if c.admin is filter_admin]
		calls = list()
		for cmds in batch(commands, 7):
			help_texts = [str(c) for c in cmds]
			calls.append(
				self._instance.chat(
					'$z$s{}'.format(' | '.join(help_texts)),
					player.login
				)
			)

		await self._instance.gbx.multicall(
			self._instance.chat(
				'$z$sCommand list. Help per command: /{}help [command]'.format('/' if filter_admin else ''),
				player.login
			),
			*calls
		)
