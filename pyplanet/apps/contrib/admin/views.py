from pyplanet.views.generics.list import ManualListView


class ModeSettingsListView(ManualListView):
	title = 'Current mode settings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui

	async def get_data(self):
		settings = []
		current_settings = await self.app.instance.mode_manager.get_settings()
		for setting in current_settings:
			settings.append(dict(name=setting,value=current_settings[setting]))
		return settings

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
				'name': 'Current Value',
				'index': 'value',
				'width': 140
			},
		]
