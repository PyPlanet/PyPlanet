from pyplanet.views import TemplateView


class DiscordLogoView(TemplateView):
	widget_x = 0
	widget_y = 90
	size_x = 50
	size_y = 50
	template_name = 'discord/discord_logo.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.app = app
		self.id = 'discord__logo'

	async def get_context_data(self):
		context = await super().get_context_data()
		context.update({
			'discord_url': self.app.join_url
		})
		return context

	async def display(self, **kwargs):
		return await super().display(**kwargs)
