from pyplanet.apps.config import AppConfig

from pyplanet.apps.contrib.queue.list import QueueList


class Queue(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.list = QueueList()
		self.list.change_hook = self.change_hook

	async def on_start(self):
		# TODO: Display widget to queue members.
		# TODO: Register settings for managing queue.
		# TODO: Commands for managing the queue.
		pass

	async def change_hook(self, action=None, entity=None, *args, **kwargs):
		print('Change hook called with action={} and entity={}'.format(action, entity))
		pass
