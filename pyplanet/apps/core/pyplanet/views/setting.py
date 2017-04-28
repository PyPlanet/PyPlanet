"""
Setting Views. Based on the Contrib component Setting.
"""
import asyncio
import re

from asyncio import Future

from pyplanet.contrib.setting.exceptions import SerializationException
from pyplanet.views import TemplateView


class SettingMenuView(TemplateView):
	template_name = 'core.pyplanet/setting/list.xml'

	def __init__(self, app, player):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		super().__init__(app.context.ui)
		self.id = 'pyplanet_settings_menu'
		self.app = app
		self.player = player

		self.page = 1
		self.per_page = 20

		self.child = None

		self.subscribe('button_close', self.close)
		self.subscribe('button_refresh', self.refresh)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_settings_data(self):
		# Displaying goes with app as heading/section, settings under it (sorted by category).
		count = len(list(self.app.instance.setting_manager.recursive_settings))
		data = await self.app.instance.setting_manager.get_apps(prefetch_values=True)
		apps = list(data.keys())

		apps, data = await self.apply_filter(apps, data)
		apps, data = await self.apply_sort(apps, data)
		apps, data = await self.apply_pagination(apps, data)

		return apps, data, count

	async def apply_filter(self, apps: list, data: dict):
		return apps, data

	async def apply_sort(self, apps: list, data: dict):
		return sorted(apps, key=lambda x: (x, x.startswith('core'))), data

	async def apply_pagination(self, apps: list, data: dict):
		# TODO: Calculate pagination.
		return apps, data

	async def get_context_data(self):
		context = await super().get_context_data()

		# Get all settings apps + categories.
		context['title'] = 'PyPlanet Settings'
		context['icon_style'] = 'Icons128x128_1'
		context['icon_substyle'] = 'ProfileAdvanced'
		context['apps'], context['data'], context['count'] = await self.get_settings_data()
		context['types'] = dict(int=int, str=str, float=float, set=set, dict=dict, list=list, bool=bool)

		return context

	async def handle_catch_all(self, player, action, values, **kwargs):
		if action.startswith('setting__'):
			match = re.search('^setting__(.+)__(.+)__(.+)$', action)
			try:
				app_label, setting_key, action = match.groups()
				manager = self.app.instance.setting_manager.get_app_manager(app_label)
				setting = await manager.get_setting(setting_key, prefetch_values=True)

				self.child = SettingEditView(self, self.player, setting)
				await asyncio.gather(
					self.hide(),
					self.child.display()
				)
				await self.child.wait_for_response()
				await self.child.destroy()
				await self.refresh()
				self.child = None
			finally:
				pass

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.
		
		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])

	async def refresh(self, *args, **kwargs):
		"""
		Refresh settings window. Will also refresh settings itself from data store.
		"""
		await self.display(**kwargs)


class SettingEditView(TemplateView):
	"""
	Setting Edit view will provide the user with a friendly edit window.
	"""
	template_name = 'core.pyplanet/setting/edit.xml'

	def __init__(self, parent, player, setting):
		"""
		Initiate child edit view.
		
		:param parent: Parent view.
		:param player: Player instance.
		:param setting: Setting instance.
		:type parent: pyplanet.view.base.View
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type setting: pyplanet.contrib.setting.setting.Setting
		"""
		super().__init__(parent.manager)
		self.id = 'pyplanet_settings_edit'
		self.parent = parent
		self.player = player
		self.setting = setting

		self.response_future = Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_save', self.save)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()
		app = None
		try:
			app = self.parent.app.instance.apps.apps[self.setting.app_label]
		except:
			pass

		context['title'] = 'Edit \'{}\''.format(self.setting)
		context['icon_style'] = 'Icons128x128_1'
		context['icon_substyle'] = 'ProfileAdvanced'

		context['app'] = app
		context['setting'] = self.setting
		context['setting_value'] = await self.setting.get_value(refresh=True)
		context['types'] = dict(int=int, str=str, float=float, set=set, dict=dict, list=list, bool=bool)

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
		raw_value = values['setting_value_field']

		try:
			await self.setting.set_value(raw_value)
		except SerializationException as e:
			await self.parent.app.instance.gbx.execute(
				'ChatSendServerMessageToLogin',
				'$z$s$fff» $fa0Error with saving setting: {}'.format(str(e)),
				player.login
			)
		except Exception as e:
			await self.parent.app.instance.gbx.execute(
				'ChatSendServerMessageToLogin',
				'$z$s$fff» $fa0Error with saving setting: {}'.format(str(e)),
				player.login
			)
		finally:
			await self.parent.app.instance.gbx.execute(
				'ChatSendServerMessageToLogin',
				'$z$s$fff» $fa0Setting has been saved \'{}\''.format(self.setting.key),
				player.login
			)
			await self.hide([player.login])
			self.response_future.set_result(self.setting)
			self.response_future.done()
