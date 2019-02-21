"""
Script Settings Views.
"""
import asyncio
from pyplanet.views import TemplateView


class ScriptSettingsView(TemplateView):
	"""
	Script Setting Edit view will provide the user with a friendly edit window.
	"""
	settings: dict
	template_name = 'admin/settings/settings.xml'

	def __init__(self, app, player, settings, descriptions, types):
		"""

		"""
		super().__init__(app.context.ui)
		self.app = app
		self.player = player
		self.settings = settings
		self.descriptions = descriptions
		self.types = types
		self.fields = [
			{
				'name': 'Config Name',
				'width': 80,
			},
			{
				'name': 'Value',
				'width': 80,
			},
			{
				'name': 'Type',
				'width': 60,
			},
		]

		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_refresh', self.refresh)
		self.subscribe('button_save', self.save)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		fields = self.fields
		left = 0
		for field in fields:
			field['left'] = left
			left += field['width']

		context = await super().get_context_data()
		context['title'] = 'Script Settings'
		context['icon'] = ''
		context['settings'] = self.settings
		context['descriptions'] = self.descriptions
		context['types'] = self.types
		context['count'] = len(self.settings)
		context['fields'] = fields
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


	async def refresh(self, player, *args, **kwargs):
		"""
		Refresh list with current properties for a specific player. Can be used to show new data changes.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		await self.display(player=player)

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


class ServerSettingsView(TemplateView):
	"""
	Server Setting Edit view will provide the user with a friendly edit window.
	"""
	settings: dict
	template_name = 'admin/settings/settings.xml'

	def __init__(self, app, player, settings, descriptions, types):
		"""

		"""
		super().__init__(app.context.ui)
		self.app = app
		self.player = player
		self.settings = settings
		self.descriptions = descriptions
		self.types = types
		self.fields = [
			{
				'name': 'Config Name',
				'width': 80,
			},
			{
				'name': 'Value',
				'width': 80,
			},
			{
				'name': 'Type',
				'width': 60,
			},
		]
		self.response_future = asyncio.Future()
		self.subscribe('button_refresh', self.refresh)
		self.subscribe('button_close', self.close)
		self.subscribe('button_save', self.save)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		left = 0
		fields = self.fields

		for field in fields:
			field['left'] = left
			left += field['width']

		context = await super().get_context_data()
		context['title'] = 'Server Settings'
		context['icon'] = ''
		context['settings'] = self.settings
		context['descriptions'] = self.descriptions
		context['types'] = self.types
		context['count'] = len(self.settings)
		context['fields'] = fields
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

	async def refresh(self, player, *args, **kwargs):
		"""
		Refresh list with current properties for a specific player. Can be used to show new data changes.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		await self.display(player=player)

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

		await self.app.instance.gbx('SetServerOptions', new_settings)
		await self.hide(player_logins=[player.login])

		self.response_future.set_result(None)
		self.response_future.done()
