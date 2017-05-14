"""
Setting Views. Based on the Contrib component Setting.
"""
import asyncio

from pyplanet.contrib.setting.exceptions import SerializationException
from pyplanet.views import TemplateView
from pyplanet.views.generics import ManualListView


class SettingMenuView(ManualListView):
	title = 'PyPlanet Settings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'ProfileAdvanced'

	def __init__(self, app, player):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		super().__init__()
		self.manager = app.context.ui
		self.app = app
		self.player = player

		self.child = None

	async def get_data(self):
		return [
			dict(
				key=setting.key,
				name=setting.name,
				app_label=setting.app_label,
				category=setting.category,
				type=setting.type,
				type_name=setting.type_name,
				value=setting._value[1],
			)
			for setting in await self.app.instance.setting_manager.get_all(prefetch_values=True)
		]

	async def open_edit_setting(self, player, values, row, **kwargs):
		if self.child:
			return

		# Getting the setting itself.
		setting = await self.app.instance.setting_manager.get_setting(row['app_label'], row['key'], prefetch_values=True)

		# Show edit view.
		self.child = SettingEditView(self, self.player, setting)
		await self.child.display()
		await self.child.wait_for_response()
		await self.child.destroy()
		await self.display()  # refresh.
		self.child = None

	async def display(self, **kwargs):
		kwargs['player'] = self.player
		return await super().display(**kwargs)

	def value_renderer(self, row, field, **kwargs):
		if row[field['index']] is None:
			return '-'
		if row['type'] == str or row['type'] == int or row['type'] == float or row['type'] == bool:
			return str(row[field['index']])
		elif row['type'] == dict:
			return 'Dictionary, edit to show'
		elif row['type'] == set or row['type'] == list:
			return '{} values, edit to show'.format(len(row[field['index']]))
		return 'Unknown type {}'.format(row['type_name'])

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 50,
				'type': 'label'
			},
			{
				'name': 'App',
				'index': 'app_label',
				'sorting': True,
				'searching': True,
				'width': 20,
				'type': 'label'
			},
			{
				'name': 'Category',
				'index': 'category',
				'sorting': True,
				'searching': True,
				'width': 20,
				'type': 'label'
			},
			{
				'name': 'Type',
				'index': 'type_name',
				'sorting': True,
				'searching': True,
				'width': 15,
				'type': 'label'
			},
			{
				'name': 'Value or contents',
				'index': 'value',
				'sorting': False,
				'searching': False,
				'width': 100,
				'type': 'label',
				'renderer': self.value_renderer,
				'action': self.open_edit_setting
			},
		]

	async def get_actions(self):
		return [
			{
				'name': 'Edit',
				'type': 'label',
				'text': '$fff &#xf040; Edit',
				'width': 11,
				'action': self.open_edit_setting,
				'safe': True
			},
		]


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

		self.response_future = asyncio.Future()

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
			await self.parent.app.instance.chat(
				'$fa0Error with saving setting: {}'.format(str(e)),
				player
			)
		except Exception as e:
			await self.parent.app.instance.chat(
				'$fa0Error with saving setting: {}'.format(str(e)),
				player
			)
		finally:
			await asyncio.gather(
				self.parent.app.instance.chat(
					'$fa0Setting has been saved \'{}\''.format(self.setting.key),
					player
				),
				self.hide([player.login])
			)
			self.response_future.set_result(self.setting)
			self.response_future.done()
