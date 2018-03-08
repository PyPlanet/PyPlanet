from pyplanet.apps.config import AppConfig

from pyplanet.apps.contrib.queue.list import QueueList


class Queue(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.list = QueueList()

	async def on_start(self):
		# TODO: Loop every spectator player and put it in the queue, then randomize the queue for the first time.
		# TODO: Register settings for managing queue.
		# TODO: Commands for managing the queue.
		# TODO: Widget for the queue.
		# TODO: Sub/pub system for queue player positioning etc.
		pass
