from pyplanet.core.events import receiver
from pyplanet.contrib.command.command import Command
from pyplanet.core import signals


class CommandManager:
	"""
	The Command Manager contributed extension is a manager that controls all chat-commands in the game.
	Your app needs to use this manager to register any custom commands you want to provide.
	"""

	def __init__(self, instance):
		self._instance = instance

		self._commands = list()

		#
		self._on_start()

	@receiver(signals.pyplanet_start_after)
	async def _on_start(self, **kwargs):
		self._on_chat()

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
