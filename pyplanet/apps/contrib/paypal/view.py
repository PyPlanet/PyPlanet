from pyplanet.views import TemplateView


class PayPalLogoView(TemplateView):
	widget_x = 0
	widget_y = 0
	template_name = 'paypal/paypal_logo.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.app = app
		self.id = 'paypal__logo'

	async def get_context_data(self):
		if 'discord' in self.app.instance.apps.apps:
			self.widget_x = 112
			self.widget_y = -50
		else:
			self.widget_x = 135
			self.widget_y = -50
		context = await super().get_context_data()
		context.update({
			'donation_url': self.app.donation_url,
			'pos_x': self.widget_x,
			'pos_y': self.widget_y
		})
		return context

	async def display(self, **kwargs):
		return await super().display(**kwargs)
