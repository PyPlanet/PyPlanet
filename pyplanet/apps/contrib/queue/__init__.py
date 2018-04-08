import logging
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.utils import style

from pyplanet.apps.contrib.queue.list import QueueList
from pyplanet.apps.contrib.queue.view import QueueView

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

logger = logging.getLogger(__name__)


class Queue(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.list = QueueList()
		self.list.change_hook = self.change_hook
		self.widget = QueueView(self)

		self.context.signals.listen(mp_signals.player.player_info_changed, self.player_change)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.player.player_disconnect, self.player_disconnect)

		self.context.signals.listen(mp_signals.player.player_enter_player_slot, self.slot_change)
		self.context.signals.listen(mp_signals.player.player_enter_spectator_slot, self.slot_change)

	async def on_start(self):
		# Register permission & command for managing queue.
		await self.instance.permission_manager.register('manage_queue', 'Clear or shuffle the queue', app=self, min_level=2)
		await self.instance.command_manager.register(
			Command('queue', target=self.command_queue_list),
			Command('clear', namespace='queue', target=self.command_queue_clear, admin=True, perms='queue:manage_queue'),
			Command('shuffle', namespace='queue', target=self.command_queue_shuffle, admin=True, perms='queue:manage_queue'),
		)

		# Make sure the spectators can't switch to player, and players can't join directly as player.
		# Also make sure the widget is displayed to the spectators.
		calls = []
		logins = []
		for player in self.instance.player_manager.online:
			if player.flow.is_spectator:
				calls.append(self.instance.gbx('ForceSpectator', player.login, 1))
				logins.append(player.login)
		if len(calls) > 0:
			await asyncio.gather(
				self.instance.gbx.multicall(*calls),
				self.widget.display(player_logins=logins)
			)

	async def on_stop(self):
		"""
		On stop will make sure the spectators can change to player slots again.
		"""
		try:
			await self.instance.gbx.multicall(*[
				self.instance.gbx('ForceSpectator', l, 0) for l in self.instance.player_manager.online_logins
			])
		except:
			pass

	async def player_change(self, player, **_):
		"""
		Player Change Signal.

		:param player: player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		:return:
		"""
		if player.flow.is_spectator and player.flow.has_player_slot:
			# Release the player slot to the game.
			try:
				await self.instance.gbx('SpectatorReleasePlayerSlot', player.login)
			except:
				# Most likely the player just left the server. Ignore and return the method.
				return
			logger.debug('Release player slot of player {}'.format(player.login))

		# Display widget if spectator.
		if player.flow.is_spectator:
			await self.widget.display(player_logins=[player.login])
		else:
			await self.widget.hide(player_logins=[player.login])

	async def player_connect(self, player, is_spectator, **_):
		"""
		Player connect signal

		:param player: Player instance
		:param is_spectator: Is player spectator?
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		if player.flow.is_server or player.flow.is_referee:
			return

		# Force player into spectator when joining as player (only when people are in the queue).
		if not is_spectator and await self.list.count() > 0:
			await self.instance.gbx.multicall(
				self.instance.gbx('ForceSpectator', player.login, 1),
				self.instance.chat(
					'$39fYou are currently forced into spectator. Use the Queue widget to obtain a player spot.', player
				)
			)
		await self.slot_change()

	async def player_disconnect(self, player, **_):
		"""
		Player Disconnect, remove from queue if in and reindex queue.

		:param player:
		:return:
		"""
		await self.exit_queue(player)
		await self.slot_change()

	async def slot_change(self, *args, **kwargs):
		"""
		Any slot changes will be captured here. We will investigate the free player spots and put a player into player
		mode if any player is in the queue and free spaces are available.
		"""
		max_players = self.instance.game.server_max_players
		num_players = self.instance.player_manager.count_players
		free_spots = max_players - num_players

		# Stop if no free spots.
		if free_spots <= 0:
			return

		with await self.list.lock:
			num_queue = await self.list.count()

			# Stop if no players are in the queue.
			if num_queue == 0:
				return

			# Pop the next player from the queue.
			next_player = await self.list.pop()
			if not next_player:
				return

			# Force player into player slot.
			await self.instance.gbx('ForceSpectator', next_player.login, 2)
			await self.instance.gbx('ForceSpectator', next_player.login, 0)

			await self.instance.chat(
				'$39fPlayer $fff{} $z$s$49f has been released from the queue! Have fun!.'.format(next_player.nickname)
			)

		# Make sure the widgets are updated for all other spectators.
		logins = [p.login for p in self.instance.player_manager.online if p.flow.is_spectator]
		await self.widget.display(player_logins=logins)

	async def change_hook(self, action=None, entity=None, *args, **kwargs):
		# Check the action of the event.
		if action in ['push', 'pop', 'remove', 'clear', 'shuffle']:
			# Reload the widget to all the players that should see it (all spectators).
			logins = [p.login for p in self.instance.player_manager.online if p.flow.is_spectator]
			await self.widget.display(player_logins=logins)

	async def enter_queue(self, player):
		"""
		Let the given player enter the queue.

		:param player: player instance
		:return: the given position or None if failed or already in the queue.
		"""
		return await self.list.push(player)

	async def exit_queue(self, player):
		"""
		Remove the player from the queue.

		:param player: player instance
		:return: Boolean determinating if the player has been removed.
		"""
		return await self.list.remove(player)

	async def command_queue_list(self, player, *args, **kwargs):
		"""
		/queue command

		:param player: Player instance
		"""
		nicknames = [style.style_strip(p.nickname, style.STRIP_SIZES, style.STRIP_COLORS) for p in await self.list.copy()]
		if nicknames:
			await self.instance.chat(
				'$39fCurrent queue: $fff{}'.format('$39f,$fff '.join(nicknames)), player
			)
		else:
			await self.instance.chat(
				'$39fThere is nobody in the waiting queue!', player
			)

	async def command_queue_clear(self, player, *args, **kwargs):
		"""
		//queue clear

		:param player: Player instance
		"""
		await self.list.clear()
		await asyncio.gather(
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has cleared the waiting queue!'.format(player.nickname)),
			self.slot_change()
		)

	async def command_queue_shuffle(self, player, *args, **kwargs):
		"""
		//queue shuffle

		:param player: Player instance
		"""
		await self.list.shuffle()
		await asyncio.gather(
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has shuffled the waiting queue!'.format(player.nickname)),
			self.slot_change()
		)
