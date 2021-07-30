"""
Custom Call Views.
"""
import asyncio
import logging

from xmlrpc.client import Fault

from pyplanet.views import TemplateView
from pyplanet.views.generics import ManualListView


class CallMenuView(ManualListView):
	title = 'Custom XMLRPC Call List'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Profile'

	def __init__(self, app, player, type='native'):
		"""
		:param app: App config instance.
		:param player: Player instance.
		:param type: Type of methods, can be 'native' or 'scripted'.
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type type: str
		"""
		super().__init__()
		self.manager = app.context.ui
		self.app = app
		self.player = player

		self.child = None

		self.type = type
		self.cache = list()

	async def get_buttons(self):
		return list()
		# return [dict(
		# 	title='Custom method',
		# 	width=35,
		# 	action=self.custom_call,
		# )]

	async def custom_call(self, player, values, **kwargs):
		pass

	async def get_data(self):
		if self.cache:
			return self.cache

		methods = await self.app.instance.gbx('system.listMethods')
		method_signatures, method_helps = await asyncio.gather(
			self.app.instance.gbx.multicall(
				*[self.app.instance.gbx('system.methodSignature', m) for m in methods]
			),
			self.app.instance.gbx.multicall(
				*[self.app.instance.gbx('system.methodHelp', m) for m in methods]
			)
		)

		self.cache = [
			dict(
				key=method,
				name=method,
				inputs=','.join(method_signature[0][1:]) if len(method_signature) and len(method_signature[0]) > 1 else '-',
				# inputs=method_signature,
				inputs_raw=method_signature[0][1:] if len(method_signature) and len(method_signature[0]) > 1 else '-',
				signature=method_signature,
				output=method_signature[0][0] if len(method_signature) and len(method_signature[0]) else '-',
				help=method_help,
				type=self.type
			)
			for method, method_signature, method_help in zip(methods, method_signatures, method_helps)
		]

		return self.cache

	async def open_call_window(self, player, values, row, **kwargs):
		if self.child:
			return

		# Getting method information.
		method = dict(
			name=row['key'],
			method=row['key'],
			signature=row['signature'],
			inputs=row['inputs_raw'],
			output=row['output'],
			help=row['help'],
			type=row['type'],
		)

		# Show edit view.
		self.child = CallActionView(self, self.player, method)
		await self.child.display()
		await self.child.wait_for_response()
		await self.child.destroy()
		self.child = None

	async def display(self, **kwargs):
		kwargs['player'] = self.player
		return await super().display(**kwargs)

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 40,
				'type': 'label'
			},
			{
				'name': 'Input(s)',
				'index': 'inputs',
				'sorting': True,
				'searching': False,
				'width': 35,
				'type': 'label'
			},
			{
				'name': 'Output',
				'index': 'output',
				'sorting': True,
				'searching': False,
				'width': 35,
				'type': 'label'
			},
			{
				'name': 'Help',
				'index': 'help',
				'sorting': False,
				'searching': True,
				'width': 75,
				'type': 'label'
			},
			{
				'name': 'Type',
				'index': 'type',
				'sorting': True,
				'searching': False,
				'width': 15,
				'type': 'label'
			},
		]

	async def get_actions(self):
		return [
			{
				'name': 'Call',
				'type': 'label',
				'text': '$fff &#xf040; Call',
				'width': 11,
				'action': self.open_call_window,
				'safe': True
			},
		]


class CallActionView(TemplateView):
	"""
	Call Action View.
	"""
	template_name = 'core.pyplanet/call/call.xml'

	def __init__(self, parent, player, method):
		"""
		Initiate child call view.

		:param parent: Parent view.
		:param player: Player instance.
		:param method: Method dictionary.
		:type parent: pyplanet.view.base.View
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:type method: dict
		"""
		super().__init__(parent.manager)
		self.parent = parent
		self.player = player
		self.method = method

		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_execute', self.execute)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()

		context['method'] = self.method

		context['title'] = 'Call \'{}\''.format(self.method['name'])
		context['icon_style'] = 'Icons128x128_1'
		context['icon_substyle'] = 'Profile'

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

	def convert_type(self, value, requested_type):
		if requested_type == 'boolean':
			return bool(value)
		elif requested_type == 'array':
			return value.splitlines()
		elif requested_type == 'double':
			return float(value)
		elif requested_type == 'int':
			return int(value)
		return value

	def format_output(self, raw_output):
		if self.method['output'] == 'array':
			return '\n'.join(raw_output)
		elif self.method['output'] == 'struct':
			return '\n'.join(['\'{}\': \'{}\''.format(key, value) for key, value in raw_output.items()])
		return raw_output

	async def execute(self, player, action, values, *_, **__):
		self.method['last_input'] = values['call_value_field']
		input_values = str(values['call_value_field']).splitlines()
		args = list()

		if len(self.method['inputs']) > 0:
			for idx, input in enumerate(self.method['inputs']):
				if len(input_values) <= idx:
					await self.parent.app.instance.chat('$ff0Warning: Not enough inputs given for the call!')
					continue

				args.append(self.convert_type(input_values[idx], input))

		# Execute call.
		try:
			logging.getLogger(__name__).warning('Executing GBX in-game: {}, {}'.format(self.method['method'], args))
			result = await self.parent.app.instance.gbx(self.method['method'], *args)
			self.method['result'] = self.format_output(result)

			# Refresh with results.
			await self.display()
		except Fault as e:
			logging.getLogger(__name__).warning('Executing GBX in-game, fault thrown: {}'.format(str(e)))
			self.method['error'] = '{}: {}'.format(e.faultCode, e.faultString)

			# Refresh with error.
			await self.display()
		except Exception as e:
			logging.getLogger(__name__).warning('Executing GBX in-game, error thrown: {}'.format(str(e)))
			await self.hide([player.login])
			self.response_future.set_result(False)
			self.response_future.done()
