import asyncio
import uuid
import logging

from asyncio import iscoroutinefunction

from pyplanet.core.events import SignalManager
from pyplanet.core.ui.template import Template

logger = logging.getLogger(__name__)


class _ManiaLink:
	def __init__(
		self, manager=None, id=None, version='3', body=None, template=None, timeout=0, hide_click=False, data=None,
		player_data=None, throw_exceptions=False
	):
		"""
		Create manialink (USE THE MANAGER CREATE, DONT INIT DIRECTLY!
		
		:param manager: Manager instance. use your app manager.
		:param id: Unique manialink id. Could be set later, must be set before displaying.
		:param version: Version of manialink.
		:param body: Body of manialink, not including manialink tags!!
		:param template: Template instance.
		:param timeout: Timeout to display, hide after the timeout is reached. Seconds.
		:param hide_click: Hide manialink when click is fired on button.
		:param data: Data to render. Could also be set later on or controlled separate from this instance.
		:param player_data: Dict with player login and for value the player specific variables. Dont fill this to have
		a global manialink instead of per person.
		:param throw_exceptions: Throw exceptions during handling and executing of action handlers.
		:type manager: pyplanet.core.ui.AppUIManager
		:type template: pyplanet.core.ui.template.Template
		:type id: str
		:type version: str
		:type timeout: int
		"""
		self.manager = manager
		self.id = id or uuid.uuid4().hex
		self.version = version
		self.body = body
		self._template = template
		self.timeout = timeout
		self.hide_click = hide_click
		self.data = data if data and isinstance(data, dict) else dict()
		self.player_data = player_data if player_data and isinstance(player_data, dict) else None
		self.throw_exceptions = False

		self.receivers = dict()

		# Register handle
		SignalManager.listen('maniaplanet:manialink_answer', self.handle)

	@property
	def is_global(self):
		return not self.player_data or len(self.player_data.keys()) == 0

	async def get_template(self):
		return self._template

	async def render(self, player_login=None, data=None, player_data=None, template=None):
		"""
		Render template. Will render template and return body.
		
		:param player_login: Render data only for player, set to None to globally render (and ignore player_data).
		:param data: Data to append.
		:param player_data: Data to append.
		:param template: Template instance to use.
		:type template: pyplanet.core.ui.template.Template
		:return: Body, rendered manialink + script.
		"""
		if data and isinstance(data, dict):
			self.data.update(data)
		if player_data and isinstance(player_data, dict):
			self.player_data.update(player_data)
		if template and isinstance(template, Template):
			self._template = template
		if not template:
			template = await self.get_template()
		if not isinstance(template, Template):
			raise Exception('Can\'t render, no template is given!')

		# Combine data (global + user specific).
		payload_data = self.data.copy()
		if player_login:
			payload_data.update(self.player_data.get(player_login, dict()))

		# Render and save in content.
		return await template.render(**payload_data)

	async def display(self, player_logins=None):
		"""
		Display the manialink. Will also render if no body is given. Will show per player or global. depending on 
		the data given and stored!
		
		:param player_logins: Only display to the list of player logins given.
		"""
		return await self.manager.send(self, player_logins)

	async def hide(self, player_logins=None):
		"""
		Hide manialink globally of only for the logins given in parameter.
		
		:param player_logins: Only hide for list of players, None for all players on the server.
		"""
		return await self.manager.hide(self, player_logins)

	def subscribe(self, action, target):
		if action not in self.receivers:
			self.receivers[action] = list()
		self.receivers[action].append(target)

	async def handle(self, player, action, values, **kwargs):
		if not action.startswith(self.id):
			return
		action_name = action[len(self.id)+2:]
		if action_name not in self.receivers:
			return await self.handle_catch_all(player, action_name, values)

		# Call receivers.
		for rec in self.receivers[action_name]:
			try:
				if iscoroutinefunction(rec):
					await rec(player, action, values)
				else:
					rec(player, action, values)
			except Exception as e:
				if self.throw_exceptions:
					raise
				else:
					logging.exception('Exception has been silenced in ManiaLink Action receiver:', exc_info=e)

	async def handle_catch_all(self, player, action, values, **kwargs):
		pass

	def __del__(self):
		try:
			SignalManager.get_signal('maniaplanet:manialink_answer').unregister(self.handle)
		except:
			pass
		asyncio.ensure_future(self.manager.destroy(self))
		self.data = None
		self.player_data = None


class StaticManiaLink(_ManiaLink):
	pass


class DynamicManiaLink(_ManiaLink):
	def __init__(self, id):
		super().__init__(id)
		raise NotImplementedError
