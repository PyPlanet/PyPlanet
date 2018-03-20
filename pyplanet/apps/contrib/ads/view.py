from pyplanet.views import TemplateView


class DiscordLogoView(TemplateView):
	widget_x = 0
	widget_y = 90
	size_x = 50
	size_y = 50
	template_name = 'ads/discord_logo.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.app = app
		self.id = 'discord__logo'

	async def get_context_data(self):
		context = await super().get_context_data()
		context.update({
			'discord_url': self.app.discord_join_url
		})
		return context

	async def display(self, **kwargs):
		return await super().display(**kwargs)


class PayPalLogoView(TemplateView):
	widget_x = 0
	widget_y = 0
	template_name = 'ads/paypal_logo.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.app = app
		self.id = 'paypal__logo'

	async def get_context_data(self):
		if await self.app.setting_enable_discord.get_value():
			self.widget_x = 121
			self.widget_y = -50
		else:
			self.widget_x = 135
			self.widget_y = -50
		context = await super().get_context_data()
		context.update({
			'donation_url': self.app.paypal_donation_url,
			'pos_x': self.widget_x,
			'pos_y': self.widget_y
		})
		return context

	async def display(self, **kwargs):
		return await super().display(**kwargs)
