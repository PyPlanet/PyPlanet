import asyncio
import math

from pyplanet.views.generics.list import ManualListView


class CommandsListView(ManualListView):
	command_manager = None

	title = 'Available chat commands'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Puzzle'

	is_admin_view = False

	data = []

	def __init__(self, command_manager, is_admin_view):
		super().__init__(self)
		self.command_manager = command_manager
		self.manager = self.command_manager._instance.ui_manager
		self.is_admin_view = is_admin_view

	async def get_fields(self):
		return [
			{
				'name': 'Command',
				'index': 'command',
				'sorting': True,
				'searching': True,
				'width': 70,
				'type': 'label'
			},
			{
				'name': 'Description',
				'index': 'description',
				'sorting': False,
				'searching': True,
				'width': 150
			},
		]

	async def get_data(self):
		data = []

		self.title = 'Available admin chat commands' if self.is_admin_view else 'Available chat commands'

		for command in [c for c in self.command_manager._commands if c.admin is self.is_admin_view]:
			command_text = ''
			if command.namespace:
				command_text += command.namespace + ' '
			command_text += command.command
			data.append({'command': command_text, 'description': command.description})

		data.sort(key=lambda c: c['command'])
		return data
