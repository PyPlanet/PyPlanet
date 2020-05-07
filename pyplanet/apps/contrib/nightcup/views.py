import asyncio
from xmlrpc.client import Fault

from pyplanet.views.generics.widget import WidgetView
from pyplanet.views import TemplateView
from pyplanet.views.generics import ManualListView

class TimerView(WidgetView):
	widget_x = 0
	widget_y = 0
	size_x = 0
	size_y = 0
	template_name = 'nightcup/timer.xml'

	def __init__(self, app):
		super().__init__()
		self.app = app
		self.manager = app.context.ui

class SettingsListView(ManualListView):
	title = 'NightCup settings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'ProfileAdvanced'

	def __init__(self, app, player):
		super().__init__()
		self.manager = app.context.ui
		self.app = app
		self.player = player
		self.sort_field = {
			'name': 'Name',
			'index': 'name',
			'sorting': True,
			'searching': True,
			'width': 60,
			'type':'label'
		}

		self.child = None

	async def get_data(self):
		return await self.app.get_long_settings()

	async def open_edit_setting(self, player, values, row, **kwargs):
		if self.child:
			return

		# Show edit view.
		self.child = ModeSettingEditView(self, self.player, row)
		await self.child.display()
		await self.child.wait_for_response()
		await self.child.destroy()
		await self.display()  # refresh.
		self.child = None

	async def display(self, **kwargs):
		# kwargs['player'] = self.player
		return await super().display(self.player)

	def value_renderer(self, row, field, **kwargs):
		value_type = type(row[field['index']])
		if row[field['index']] is None:
			return '-'
		if value_type == str or value_type == int or value_type == float or value_type == bool:
			return str(row[field['index']])
		elif value_type == dict:
			return 'Dictionary, edit to show'
		elif value_type == set or value_type == list:
			return '{} values, edit to show'.format(len(row[field['index']]))
		return 'Unknown type {}'.format(str(value_type))

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 60,
				'type': 'label'
			},
			{
				'name': 'Description',
				'index': 'description',
				'sorting': False,
				'searching': True,
				'width': 75,
				'type': 'label',
			},
			{
				'name': 'Value or contents',
				'index': 'value',
				'sorting': False,
				'searching': False,
				'width': 70,
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


class ModeSettingEditView(TemplateView):
	template_name = 'admin/setting/edit.xml'

	def __init__(self, parent, player, setting):
		super().__init__(parent.manager)
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
		context['title'] = 'Edit \'{}\''.format(self.setting['name'])
		context['icon_style'] = 'Icons128x128_1'
		context['icon_substyle'] = 'ProfileAdvanced'

		context['setting'] = self.setting
		context['setting_value'] = self.setting['value']
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
		value = values['setting_value_field']

		try:
			settings_long = (await self.parent.get_data())
			settings = {setting['name']: setting['value'] for setting in settings_long}
			settings[self.setting['name']] = int(value)
			await self.parent.app.update_settings(settings)
		except ValueError:
			message = '$i$f00You have entered a value with a wrong type.'
			await self.parent.app.instance.chat(message, player)
			return
		finally:
			await asyncio.gather(
				self.parent.app.instance.chat(
					'$ff0Changed nightcup setting "$fff{}$ff0" to "$fff{}$ff0" (was: "$fff{}$ff0").'.format(
						self.setting['name'], value, self.setting['value']
					),
					player
				),
				self.hide([player.login])
			)
			self.response_future.set_result(self.setting)
			self.response_future.done()
