import asyncio

from pyplanet.views import TemplateView
from pyplanet.views.generics.list import ManualListView


class CommandsListView(ManualListView):
	title = 'Available chat commands'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Puzzle'

	is_admin_view = False

	data = []

	def __init__(self, app, player, is_admin_view):
		super().__init__(self)
		self.app = app
		self.instance = app.instance
		self.manager = app.context.ui
		self.player = player
		self.is_admin_view = is_admin_view

		self.child = None

	async def get_fields(self):
		return [
			{
				'name': 'Command',
				'index': 'command',
				'sorting': True,
				'searching': True,
				'width': 70,
				'type': 'label',
				'action': self.open_command_details
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

		for command in [c for c in self.instance.command_manager._commands if c.admin is self.is_admin_view]:
			if not self.is_admin_view or await command.has_permission(self.instance, self.player):
				command_text = ''
				if command.namespace:
					command_text += '|'.join(command.namespace) if isinstance(command.namespace, (list, tuple)) else command.namespace
					command_text += ' '
				command_text += command.command
				data.append({'command': command_text, 'description': command.description, 'command_object': command})

		data.sort(key=lambda c: c['command'])
		return data

	async def display(self, **kwargs):
		kwargs['player'] = self.player
		return await super().display(**kwargs)

	async def open_command_details(self, player, values, row, **kwargs):
		if self.child:
			return

		# Show details view.
		self.child = CommandDetailsView(self, self.player, row['command_object'])
		await self.child.display()
		await self.child.wait_for_response()
		await self.child.destroy()
		await self.display()  # refresh.
		self.child = None


class CommandDetailsView(TemplateView):
	template_name = 'core.pyplanet/command/details.xml'

	def __init__(self, parent, player, command):
		"""
		Initiate child edit view.

		:param parent: Parent view.
		:param player: Player instance.
		:param command: Command instance.
		:type parent: pyplanet.view.base.View
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type command: pyplanet.contrib.command.Command
		"""
		super().__init__(parent.manager)
		self.parent = parent
		self.player = player
		self.command = command

		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()
		context['command_chat'] = str(self.command)
		context['command'] = self.command

		return context

	async def wait_for_response(self):
		return await self.response_future

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
