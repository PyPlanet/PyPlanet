"""
Queue View.
"""
from pyplanet.apps.contrib.queue.exception import PlayerAlreadyInQueue
from pyplanet.views import TemplateView


class QueueView(TemplateView):
	"""
	Queue View
	"""
	template_name = 'queue/queue.xml'

	def __init__(self, app):
		"""
		Initiate the queue view.

		:param app: Queue app instance.
		:type app: pyplanet.apps.contrib.queue.Queue
		"""
		super().__init__(app.context.ui)

		self.app = app
		self.id = 'queue_widget'

		self.subscribe('enter', self.enter_queue)
		self.subscribe('exit', self.exit_queue)

	async def enter_queue(self, player, *_, **__):
		try:
			await self.app.enter_queue(player)
			await self.app.slot_change()
		except PlayerAlreadyInQueue:
			pass

	async def exit_queue(self, player, *_, **__):
		await self.app.exit_queue(player)

	async def get_context_data(self):
		context = await super().get_context_data()
		context['total'] = await self.app.list.count()
		return context

	async def get_per_player_data(self, login):
		try:
			player = await self.app.instance.player_manager.get_player(login=login)
			return dict(
				position=await self.app.list.get_position(player)
			)
		except:
			return dict(
				position=None
			)
