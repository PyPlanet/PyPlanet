from pyplanet.apps.config import AppConfig
from pyplanet.core.events import receiver, SignalManager
from pyplanet.contrib.command import CommandManager


class ManiaplanetConfig(AppConfig):
	name = 'pyplanet.apps.core.maniaplanet'
	core = True

	def on_ready(self):
		# Register receivers context, only required if you use classmethods.
		self.on_chat()

		# Register commands.


	@receiver('maniaplanet:player_chat')
	async def on_chat(self, chat, *args, **kwargs):
		print('ENDING IN SIGNAL THISONE', self.label)
		print(chat)
