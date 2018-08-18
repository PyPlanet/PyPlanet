"""
Script Settings Views.
"""
import asyncio
from xmlrpc.client import Fault

from pyplanet.contrib.setting.exceptions import SerializationException
from pyplanet.views import TemplateView
from pyplanet.views.generics import ManualListView


class ScriptSettingsView(TemplateView):
	"""
	Script Setting Edit view will provide the user with a friendly edit window.
	"""
	settings: dict
	template_name = 'admin/settings/settings.xml'

	def __init__(self, app, player, settings):
		"""

		"""
		super().__init__(app.context.ui)
		self.app = app
		self.player = player
		self.settings = settings
		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_save', self.save)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()
		context['title'] = 'Script Settings'
		context['icon_style'] = 'Icons128x128_1'
		context['icon_substyle'] = 'ProfileAdvanced'
		context['settings'] = self.settings
		return context

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])
		self.response_future.set_result(None)
		self.response_future.done()

	async def wait_for_response(self):
		return await self.response_future

	async def save(self, player, action, values, *args, **kwargs):
		new_settings = {}

		for key, value in self.settings.items():
			in_value = values[key]

			if isinstance(value, float):
				in_value = float(in_value)
			if isinstance(value, int):
				in_value = int(in_value)
			if isinstance(value, bool):
				lower_setting_value = str(in_value).lower()
				if lower_setting_value == 'true' or lower_setting_value == '1':
					in_value = True
				else:
					in_value = False

			new_settings[key] = in_value

		await self.app.instance.mode_manager.update_settings(new_settings)

		await self.hide(player_logins=[player.login])

		self.response_future.set_result(None)
		self.response_future.done()
