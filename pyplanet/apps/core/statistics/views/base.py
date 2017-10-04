from pyplanet.views import TemplateView


class StatsView(TemplateView):
	def __init__(self, manager, player, *args, **kwargs):
		self.player = player
		super().__init__(manager, *args, **kwargs)

	def display(self, *args, **kwargs):
		return super().display([self.player.login], **kwargs)
