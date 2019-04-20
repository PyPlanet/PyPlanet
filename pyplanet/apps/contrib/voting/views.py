from pyplanet.views.generics.widget import WidgetView


class VoteWidget(WidgetView):
	"""
	Voting widget.
	"""

	widget_x = -25
	widget_y = -58.5
	template_name = 'voting/voting.xml'

	def __init__(self, app):
		"""
		Initializes the widget.

		:param app: the voting application (plugin)
		"""
		
		super().__init__(app.context.ui)
		self.app = app
		self.id = 'pyplanet__widgets_voting'

		self.subscribe('yes', self.vote_yes)
		self.subscribe('no', self.vote_no)

	async def get_context_data(self):
		"""
		Called to request data to display in the widget.
		Will return the type of vote currently running.
		"""

		context = await super().get_context_data()

		context.update({
			'vote_type': self.app.current_vote.action
		})

		return context

	async def vote_yes(self, player, *args, **kwargs):
		"""
		Called when a player votes yes via the widget (either via button or F5).

		:param player: player who voted
		"""

		await self.app.vote_yes(player, None)

	async def vote_no(self, player, *args, **kwargs):
		"""
		Called when a player votes no via the widget (either via button or F6).

		:param player: player who voted
		"""
		
		await self.app.vote_no(player, None)
