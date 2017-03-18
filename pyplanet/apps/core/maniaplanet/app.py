from pyplanet.apps.config import AppConfig
from pyplanet.core.events import receiver, Manager


class ManiaplanetConfig(AppConfig):
	name = 'pyplanet.apps.core.maniaplanet'
	core = True

	def on_ready(self):
		pass

	@staticmethod
	@receiver('maniaplanet:player_chat')
	def on_chat(chat, **kwargs):
		print('ENDING IN SIGNAL THISONE')
		print(chat)
