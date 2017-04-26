"""
Setting Views. Based on the Contrib component Setting.
"""
from pyplanet.views import TemplateView


class SettingView(TemplateView):
	template_package = 'pyplanet.apps.core.pyplanet'
	template_name = 'setting/overview.xml'

	def __init__(self, app, player):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		super().__init__(app.context.ui)
		self.id = 'pyplanet_settings_overview'
		self.app = app
		self.player = player

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()

		# Get all settings apps + categories.
		context['categories'] = self.app.context.setting.get_categories()
		context['apps'] = self.app.context.setting.get_apps()

		return context
