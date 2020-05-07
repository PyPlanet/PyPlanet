from pyplanet.views.generics.widget import WidgetView
from pyplanet.views.generics.list import ManualListView

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
		return await self.app.get_settings()

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
