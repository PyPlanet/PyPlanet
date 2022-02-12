"""
Donation Toolbar View.
"""

from pyplanet.views.generics.widget import WidgetView


class DonationToolbarWidget(WidgetView):
	template_name = 'transactions/donation_toolbar.xml'

	widget_x = -109.5
	widget_y = 61
	z_index = 130
	game = None

	def __init__(self, app):
		"""
		Initiate the toolbar view.

		:param app: App instance.
		:type app: pyplanet.apps.contrib.transactions.Transactions
		"""
		super().__init__(app.context.ui)

		self.app = app
		self.id = 'donate_widget'

		self.subscribe('bar_button_100P', self.action_donate(100))
		self.subscribe('bar_button_500P', self.action_donate(500))
		self.subscribe('bar_button_1000P', self.action_donate(1000))
		self.subscribe('bar_button_2000P', self.action_donate(2000))
		self.subscribe('bar_button_5000P', self.action_donate(5000))

	async def display(self, player=None, **kwargs):
		if not self.game:
			self.game = self.app.instance.game.game
			if self.game == 'sm':
				self.widget_x = -145

		return await super().display(player, **kwargs)

	async def get_context_data(self):
		data = await super().get_context_data()
		data['game'] = self.app.instance.game.game
		return data

	def action_donate(self, planets):
		async def donate(player, *args, **kwargs):
			return await self.app.instance.command_manager.execute(player, '/donate {}'.format(planets))
		return donate
