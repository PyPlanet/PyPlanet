import textwrap

from pyplanet.contrib import CoreContrib
from pyplanet.contrib.command.command import Command


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
		self._instance.signals.listen('maniaplanet:player_chat', self._on_chat)

	async def register(self, *commands):
		"""
		Register your command.

		:param commands: Command instance.
		:type commands: pyplanet.contrib.command.command.Command
		"""
		self._commands.extend(commands)

	async def execute(self, player, command, *args):
		"""
		Execute a command for the given player with the given args.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:param command: Command instance.
		:type command: pyplanet.contrib.command.command.Command
		:param args: Args for the command, will be concat into a string with spaces.
		:return:
		"""
		if isinstance(command, Command):
			command_text = '//' if command.admin else '/'
			if command.namespace:
				command_text += command.namespace + ' '
			command_text += command.command
		else:
			command_text = command

		return await self._on_chat(player, ' '.join([command_text] + list(args)), True)

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

	async def get_command_by_command_text(self, command):
		"""
		Get command by command text. (Used in the /help command)

		:param command: Command entry, array of strings (split by spaces).
		:return: Command object.
		"""
		# Find the right command.
		for cmd in self._commands:
			if cmd.match(command):
				return cmd
		return None

	async def help_entries(self, player, admin_only):  # pragma: no cover
		"""
		Get all help entries for the player.

		:param player: Player instance.
		:param admin_only: Only the admin commands or non-admin. True for admin only, False for player only.
						Will filter on permissions of the player as well!
		:return: List of commands objects.
		"""
		# All commands.
		commands = [c for c in self._commands if c.admin is admin_only]
		if admin_only:
			commands = [c for c in commands if await c.has_permission(self._instance, player)]

		return commands
