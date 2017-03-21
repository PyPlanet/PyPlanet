from pyplanet.core.events import receiver
from .command import Command
from pyplanet.core import signals


class _CommandManager:
	def __init__(self):
		self.commands = list()

		self.on_start()
		self.on_chat()

	@receiver(signals.pyplanet_start)
	async def on_start(self, **kwargs):
		pass

	@receiver('maniaplanet:player_chat')
	async def on_chat(self, player, text, **kwargs):
		pass


CommandManager = _CommandManager()
