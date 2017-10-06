from pyplanet.views import TemplateView


class VoteWidget(TemplateView):

	template_name = 'voting/voting.xml'

	def __init__(self, app):
		super().__init__(app.context.ui)
		self.app = app
		self.id = 'pyplanet__widgets_voting'

		self.subscribe('yes', self.vote_yes)
		self.subscribe('no', self.vote_no)

	async def get_context_data(self):
		return await super().get_context_data()

	async def vote_yes(self, player, *args, **kwargs):
		await self.app.vote_yes(player, None)

	async def vote_no(self, player, *args, **kwargs):
		await self.app.vote_no(player, None)
