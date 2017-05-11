from pyplanet.views import TemplateView


class LogoView(TemplateView):
	template_name = 'core.pyplanet/logo.xml'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.id = 'pyplanet__logo'

	async def display(self, **kwargs):
		return await super().display(**kwargs)
