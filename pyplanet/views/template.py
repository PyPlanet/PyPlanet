import asyncio

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core import Controller
from pyplanet.core.ui.template import load_template
from pyplanet.utils.codeutils import deprecated
from pyplanet.views.base import View


class TemplateView(View):
	"""
	The TemplateView will provide a view based on a XML template (ManiaLink for example).
	The view contains some class properties that are required to work. Those are described bellow.

	To use the TemplateView. Initiate it in your own View class, and override one of the following methods:

	:method get_context_data(): Return the global context data here.
								Make sure you use the super() to retrieve the current context.
	:method get_all_player_data(logins): Retrieve the player specific dictionary.
										Return dict with player as key and value should contain the data dict.
	:method get_per_player_data(login): Retrieve the player specific dictionary per player.
										Return dict with the data dict for the specific login (player).
	:method get_template(): Return the template instance from Jinja2. You mostly should not override this method.

	As alternative you can manipulate the instance.data and instance.player_data too.

	**Properties that are useful to change**:

	:prop data: Global context data. Dict.
	:prop player_data: Player context data. Dict with player as key.
	:prop hide_click: Should the manialink disappear after clicking a button/text.
	:prop timeout: Timeout to hide manialink in seconds.

	**Example usage:**

	.. code-block:: python

		class AlertView(TemplateView):
			template_name = 'my_app/test.xml' # template should be in: ./my_app/templates/test.xml
			# Some prefixes that can be used in the template_name:
			#
			# - core.views: ``pyplanet.views.templates``.
			# - core.pyplanet: ``pyplanet.apps.core.pyplanet.templates``.
			# - core.maniaplanet: ``pyplanet.apps.core.pyplanet.templates``.
			# - core.trackmania: ``pyplanet.apps.core.trackmania.templates``.
			# - core.shootmania: ``pyplanet.apps.core.shootmania.templates``.
			# - [app_label]: ``[app path]/templates``.

			async def get_context_data(self):
				context = await super().get_context_data()
				context['title'] = 'Sample'
				return context

	"""

	template_name = None

	async def get_context_data(self):
		"""
		Get global and local context data, used to render template.
		"""
		context = dict(
			id=self.id
		)
		return context

	@deprecated
	async def get_player_data(self):
		"""
		Get data per player, return dict with login => data dict.

		.. deprecated:: 0.4.0
			Use :func:`get_per_player_data` and :func:`get_all_player_data` instead. Will be removed in 0.6.0!

		"""
		return dict()

	async def get_all_player_data(self, logins):
		"""
		Get all player data, should return dictionary with login as key, and dict as value.

		:param logins: Login list of players. String list.
		:return: Dictionary with data.
		"""
		return dict()

	async def get_per_player_data(self, login):
		"""
		Get data for specific player. Will be called for all players that will render the xml for.

		:param login: Player login string.
		:return: Dictionary or None to ignore.
		:type login: str
		"""
		return dict()

	async def get_template(self):
		return await load_template(self.template_name)

	async def render(self, *args, player_login=None, **kwargs):
		"""
		Render template for player. This will only render the body and return it. Not send it!

		:param player_login: Render data only for player, set to None to globally render (and ignore player_data).
		:return: Body, rendered manialink + script.
		"""
		kwargs['data'] = await self.get_context_data()
		kwargs['player_login'] = player_login
		kwargs['player_data'] = self.player_data # Should already been read by display().
		kwargs['template'] = await self.get_template()
		return await super().render(*args, **kwargs)

	async def display(self, player_logins=None, **kwargs):
		"""
		Display the manialink. Will also render if no body is given. Will show per player or global. depending on
		the data given and stored!

		:param player_logins: Only display to the list of player logins given.
		"""
		# Get player data (old way).
		self.player_data = await self.get_player_data()

		self.player_data.update(await self.get_all_player_data(
			player_logins or [p.login for p in Controller.instance.player_manager.online]
		))

		# Get player data (new way).
		async def get_player_data(login):
			data = await self.get_per_player_data(login)
			if not data or isinstance(data, dict) and len(data.keys()) == 0:
				data = None
			return login, data

		player_data = await asyncio.gather(*[
			get_player_data(p.login) if isinstance(p, Player) else get_player_data(p)
			for p in player_logins or Controller.instance.player_manager.online
		])

		# TODO: This can be flatten with `self.player_data = dict(player_data)` after deprecated code has been removed.
		for login, data in player_data:
			if not isinstance(data, dict) or len(data.keys()) == 0:
				continue
			if login in self.player_data and isinstance(self.player_data[login], dict):
				self.player_data[login].update(data)
			else:
				self.player_data[login] = data

		# Fallback in case the data is empty or not a dictionary.
		if not isinstance(self.player_data, dict):
			self.player_data = dict()

		return await super().display(player_logins, **kwargs)
