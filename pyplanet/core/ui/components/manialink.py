import asyncio
import uuid
import logging

from asyncio import iscoroutinefunction

from pyplanet.core.events import SignalManager
from pyplanet.core.ui.exceptions import ManialinkMemoryLeakException
from pyplanet.core.ui.template import Template

logger = logging.getLogger(__name__)


class _ManiaLink:
	def __init__(
		self, manager=None, id=None, version='3', body=None, template=None, timeout=0, hide_click=False, data=None,
		player_data=None, disable_alt_menu=False, throw_exceptions=False, relaxed_updating=False,
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
		:param relaxed_updating: Relaxed updating will rate limit the amount of updates send to clients.
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
		self.player_data = player_data if player_data and isinstance(player_data, dict) else dict()
		self.throw_exceptions = False
		self.disable_alt_menu = bool(disable_alt_menu)
		self.relaxed_updating = relaxed_updating

		self.receivers = dict()
		self._is_global_shown = False
		self._is_player_shown = dict()  # Holds per player login a boolean if the ml is shown.

		self.__register_listener = False

	async def is_global(self):
		return not self.player_data or self.player_data.keys() == 0

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
		if not player_data:
			player_data = self.player_data or dict()
		if template and isinstance(template, Template):
			self._template = template
		if not template:
			template = await self.get_template()
		if not isinstance(template, Template):
			raise Exception('Can\'t render, no template is given!')

		# Combine data (global + user specific).
		payload_data = self.data.copy()
		if player_login:
			payload_data.update(player_data.get(player_login, dict()))

		# Render and save in content.
		return await template.render(**payload_data)

	async def display(self, player_logins=None, **kwargs):
		"""
		Display the manialink. Will also render if no body is given. Will show per player or global. depending on
		the data given and stored!

		:param player_logins: Only display to the list of player logins given.
		"""
		if player_logins:
			for login in player_logins:
				self._is_player_shown[login] = True
		else:
			self._is_global_shown = True

		if not self.__register_listener:
			# Register handle
			SignalManager.listen('maniaplanet:manialink_answer', self.handle)
			self.__register_listener = True

		return await self.manager.send(self, player_logins, **kwargs)

	async def hide(self, player_logins=None):
		"""
		Hide manialink globally of only for the logins given in parameter.

		:param player_logins: Only hide for list of players, None for all players on the server.
		"""
		if player_logins:
			for login in player_logins:
				try:
					del self._is_player_shown[login]
				except:
					pass
		else:
			self._is_global_shown = False

		return await self.manager.hide(self, player_logins)

	def subscribe(self, action, target):
		"""
		Subscribe to a action given by the manialink.

		:param action: Action name.
		:param target: Target method.
		:return:
		"""
		if action not in self.receivers:
			self.receivers[action] = list()
		self.receivers[action].append(target)

	async def handle(self, player, action, values, **kwargs):
		if not action.startswith(self.id):
			return

		if not self._is_global_shown and player.login not in self._is_player_shown.keys():
			# Ignore if id is unique (uuid4)
			try:
				uuid.UUID(self.id, version=4)
			except:
				raise ManialinkMemoryLeakException(
					'Old view instance (ml-id: {}) is not yet destroyed, but is receiving player callbacks!, '
					'Make sure you are not removing old view instances with .destroy() and del variable! '
					'Potential Memory Leak!! Should be fixed asap!'.format(self.id)
				)

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
		"""
		Override this class to handle all other actions related to this view/manialink.

		:param player: Player instance.
		:param action: Action name/string
		:param values: Values provided by the user client.
		:param kwargs: *
		"""
		pass

	async def destroy(self):
		"""
		Destroy the Manialink with it's handlers and references.
		Will also hide the Manialink for all users!
		"""
		try:
			SignalManager.get_signal('maniaplanet:manialink_answer').unregister(self.handle)
		except Exception as e:
			logging.exception(e)
		try:
			await self.manager.destroy(self)
		except:
			pass
		self.receivers = dict()
		self.data = None
		self.player_data = None

	def destroy_sync(self):
		"""
		Destroy the Manialink with it's handlers and references.
		Will also hide the Manialink for all users!

		This method is sync and will call a async method (destroying of the manialink at our players) async but will not
		be executed at the same time. Be aware with this one!
		"""
		try:
			SignalManager.get_signal('maniaplanet:manialink_answer').unregister(self.handle)
			asyncio.ensure_future(self.manager.destroy(self))
		except Exception as e:
			logging.exception(e)
		self.receivers = dict()
		self.data = None
		self.player_data = None

	def __del__(self):
		self.destroy_sync()


class StaticManiaLink(_ManiaLink):
	"""
	The StaticManiaLink is mostly used in PyPlanet for general views. Please use the ``View`` classes instead of this
	core ui component!
	"""
	pass


class DynamicManiaLink(_ManiaLink):
	"""
	The DynamicManiaLink is a special manialink with data-bindings and automatically updates via maniascript.
	Please use the ``View`` classes instead!

	.. warning ::

		This feature is not yet implemented.

	"""
	def __init__(self, id):
		super().__init__(id)
		raise NotImplementedError
