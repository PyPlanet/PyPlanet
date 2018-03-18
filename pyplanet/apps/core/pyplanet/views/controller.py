from pyplanet.views import TemplateView


class ControllerView(TemplateView):
	template_name = 'core.pyplanet/controller.xml'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.id = 'pyplanet__controller'

	async def get_context_data(self):
		from pyplanet.core import Controller
		context = await super().get_context_data()
		context['game'] = Controller.instance.game.game
		return context

	async def display(self, **kwargs):
		return await super().display(**kwargs)
