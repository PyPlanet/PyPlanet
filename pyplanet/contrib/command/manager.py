from pyplanet.core.events import receiver
from pyplanet.contrib.command.command import Command
from pyplanet.core import signals


class CommandManager:
	"""
	The Command Manager contributed extension is a manager that controls all chat-commands in the game.
	Your app needs to use this manager to register any custom commands you want to provide.
	"""

	def __init__(self, instance):
		"""
		Init manager.
		
		:param instance: Controller Instance
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		self._commands = list()

		#
		self._on_start()

	@receiver(signals.pyplanet_start_after)
	async def _on_start(self, **kwargs):
		self._on_chat()

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

	@receiver('maniaplanet:player_chat')
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

		# Try to match the command prefix by one of the registered commands.
		command = None
		for cmd in self._commands:
			if cmd.match(argv):
				command = cmd
				break

		# Let the command handle the logic it needs.
		if command:
			await command.handle(self._instance, player, argv)

	async def _help(self, player, data, raw, command):
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
				await self._instance.gbx.execute(
					'ChatSendServerMessageToLogin',
					'$z$s >> {}'.format(cmd_instance.usage_text),
					player.login
				)
				return

		# All commands.
		commands = [c for c in self._commands if c.admin is filter_admin]
		commands_string = ', '.join([str(c) for c in commands])

		await self._instance.gbx.multicall(
			self._instance.gbx.prepare(
				'ChatSendServerMessageToLogin',
				'$z$s >> Command list. Help per command: /{}help [command]'.format('/' if filter_admin else ''),
				player.login
			),
			self._instance.gbx.prepare(
				'ChatSendServerMessageToLogin',
				'$z$s >> {}'.format(commands_string),
				player.login
			)
		)
