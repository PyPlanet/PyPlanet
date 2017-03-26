from pyplanet.core.events import receiver
from pyplanet.contrib.command.command import Command
from pyplanet.core import signals


class CommandManager:
	def __init__(self, instance):
		self._instance = instance

		self.commands = list()

		self.on_start()
		self.on_chat()

	@receiver(signals.pyplanet_start_after)
	async def on_start(self, **kwargs):
		tst_cmd = Command(command='ok', target=self.target, perms='core.pyplanet:use_ok', admin=True)
		tst_cmd.add_param('times', type=int)

		self.commands.extend([
			tst_cmd
		])

	async def target(self, player, data, **kwargs):
		await self._instance.gbx.execute(
			'ChatSendServerMessageToLogin',
			'$z$s >> You just did /ok. Parameters we got: {}'.format(str(data)),
			player.login
		)

	@receiver('maniaplanet:player_chat')
	async def on_chat(self, player, text, cmd, **kwargs):
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
		for cmd in self.commands:
			if cmd.match(argv):
				command = cmd
				break

		# Let the command handle the logic it needs.
		if command:
			await command.handle(self._instance, player, argv)
