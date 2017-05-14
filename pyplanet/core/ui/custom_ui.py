"""
The Custom UI will be set and hold in the class definition bellow. Per player and global!
"""
import asyncio

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.signals import pyplanet_start_after


class CustomUI:  # pragma: no cover
	"""
	Access this class with:

	.. code-block:: python

		self.instance.ui_manager.custom_ui

	See: http://undef.name/Development/Manialinks.php#CustomUi
	
	"""
	TEMPLATE = """
	<custom_ui>
		<notice visible="{notice}" />
		<challenge_info visible="{challenge_info}"/>
		<net_infos visible="{net_infos}"/>
		<chat visible="{chat}"/>
		<checkpoint_list visible="{checkpoint_list}"/>
		<round_scores visible="{round_scores}"/>
		<scoretable visible="{scoretable}"/>
		<global visible="{all}"/>
	</custom_ui>
	"""

	def __init__(self, instance):
		self._instance = instance

		self._global_options = dict(
			notice=True, challenge_info=True, net_infos=True, chat=True, checkpoint_list=True, round_scores=True,
			scoretable=True, all=True
		)
		self._player_options = dict()

	async def on_start(self):
		self._instance.signal_manager.listen('maniaplanet:player_connect', self.player_connect)
		self._instance.signal_manager.listen('maniaplanet:player_disconnect', self.player_disconnect)
		self._instance.signal_manager.listen(pyplanet_start_after, self.on_ready)

	async def on_ready(self, **kwargs):
		for player in self._instance.player_manager.online:
			self._player_options[player.login] = self._global_options.copy()
		await self.send()

	async def player_connect(self, player, **kwargs):
		self._player_options[player.login] = player_ui = self._global_options.copy()

		# Send the custom UI props to the player.
		await self.send(player)

	async def player_disconnect(self, player, **kwargs):
		if player.login in self._player_options:
			try:
				del self._player_options[player.login]
			except:
				pass

	def set_global(self, option, value):
		"""
		Set a global and default option, for all players.
		
		:param option: Option name
		:param value: Display value
		"""
		self._global_options[option] = value
		for ui in self._player_options.values():
			ui[option] = value

	def set(self, player, option, value):
		"""
		Set option for specific player.
		
		:param player: Player login or instance.
		:param option: Option name
		:param value: Value
		"""
		if isinstance(player, Player):
			player = player.login
		if player not in self._player_options:
			self._player_options[player] = self._global_options.copy()
		self._player_options[player][option] = value

	def get_global(self, option):
		"""
		Get the global option value
		
		:param option: Option name
		:return: Boolean or other value.
		"""
		return self._global_options.get(option, None)

	def get(self, player, option):
		"""
		Get the player option value
		
		:param player: Player instance or login string.
		:param option: Option name
		:return: Boolean or other value.
		"""
		if isinstance(player, Player):
			player = player.login
		if player not in self._player_options:
			return None
		return self._player_options[player].get(option, None)

	async def send(self, player=None, **kwargs):
		"""
		Send the custom UI to one player or all.
		"""
		if not player:
			return await asyncio.gather(*[
				self.send(l) for l in self._player_options.keys()
			])

		if isinstance(player, Player):
			player = player.login
		if not isinstance(player, str):
			return
		if player not in self._player_options:
			return

		body = '<manialinks>{}</manialinks>'.format(self.TEMPLATE.format(**self._player_options[player]))
		return await self._instance.gbx('SendDisplayManialinkPageToLogin', player, body, 0, False)
