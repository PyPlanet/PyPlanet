"""
Mode Settings Views.
"""
import asyncio
from xmlrpc.client import Fault

from pyplanet.contrib.setting.exceptions import SerializationException
from pyplanet.views import TemplateView
from pyplanet.views.generics import ManualListView


class ModeSettingMenuView(ManualListView):
	title = 'Mode Settings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'ProfileAdvanced'

	def __init__(self, app, player):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:type app: pyplanet.apps.contrib.admin.Admin
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
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
			'type': 'label'
		}

		self.child = None

	async def get_data(self):
		settings = dict()
		mode_info = await self.app.instance.mode_manager.get_current_script_info()
		mode_settings = await self.app.instance.mode_manager.get_settings()
		if 'ParamDescs' in mode_info:
			for info in mode_info['ParamDescs']:
				real_type = str
				if info['Type'] == 'boolean':
					real_type = bool
				elif info['Type'] == 'int':
					real_type = int
				elif info['Type'] == 'double':
					real_type = float

				settings[info['Name']] = dict(
					default=info['Default'], type=real_type, name=info['Name'], description=info['Desc']
				)

		for name, value in mode_settings.items():
			if name not in settings:
				settings[name] = dict(default=None, type=None, description='-')
			settings[name]['name'] = name
			settings[name]['value'] = value
			if not settings[name]['type']:
				settings[name]['type'] = type(value)
		return list(settings.values())

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
		kwargs['player'] = self.player
		return await super().display(**kwargs)

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
	"""
	Mode Setting Edit view will provide the user with a friendly edit window.
	"""
	template_name = 'admin/setting/edit.xml'

	def __init__(self, parent, player, setting):
		"""
		Initiate child edit view.

		:param parent: Parent view.
		:param player: Player instance.
		:param setting: Setting dictionary.
		:type parent: pyplanet.view.base.View
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type setting: dict
		"""
		super().__init__(parent.manager)
		self.id = 'pyplanet_mode_settings_edit'
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
			current_value = self.setting['value']
			current_type = type(current_value)

			if isinstance(current_value, bool):
				lower_setting_value = str(value).lower()

				if lower_setting_value == 'true' or value == '1':
					value = True
				elif lower_setting_value == 'false' or value == '0':
					value = False
				else:
					raise ValueError
			value = current_type(value)

			await self.parent.app.instance.mode_manager.update_settings({
				self.setting['name']: value
			})
		except ValueError:
			message = '$i$f00Unable to cast "$fff{}$f00" to required type ($fff{}$f00) for "$fff{}$f00".'.format(
				value, self.setting['type'], self.setting['name']
			)
			await self.parent.appinstance.chat(message, player)
			return
		except Fault as exception:
			message = '$i$f00Unable to set "$fff{}$f00" to "$fff{}$f00": $fff{}$f00.'.format(
				self.setting['name'], value, exception
			)
			await self.parent.app.instance.chat(message, player)
			return
		finally:
			await asyncio.gather(
				self.parent.app.instance.chat(
					'$ff0Changed mode setting "$fff{}$ff0" to "$fff{}$ff0" (was: "$fff{}$ff0").'.format(
						self.setting['name'], value, self.setting['value']
					),
					player
				),
				self.hide([player.login])
			)
			self.response_future.set_result(self.setting)
			self.response_future.done()
