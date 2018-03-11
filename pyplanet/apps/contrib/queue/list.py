"""
The list module contains the class to hold all the queued players.
"""

import asyncio
from random import shuffle

from pyplanet.apps.contrib.queue.exception import PlayerAlreadyInQueue


class QueueList:
	"""
	The Queue List holds the actual queue and manages it's list thread-safe.
	"""

	def __init__(self):
		self.list = list()
		self._lock = asyncio.Lock()
		self.lock = asyncio.Lock()

		self.change_hook = None

	async def push(self, player):
		"""
		Push a player in the last place of the queue. Return the place of the player.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: Returns the index of the player (the textual position is index+1).
		:rtype: int
		"""
		with await self._lock:
			# Make sure the player is not yet in the queue.
			try:
				index = self.list.index(player)
				raise PlayerAlreadyInQueue('Player {} already in queue on position {} (index: {})'.format(player.login, index+1, index))
			except ValueError:
				pass

			# Add the player to the queue.
			self.list.append(player)
			index = self.list.index(player)

		# Call change hook.
		if self.change_hook and callable(self.change_hook):
			await self.change_hook(action='push', entity=player)

		return index

	async def count(self):
		"""
		Get the current count of the queue.

		:return: Count of list.
		:rtype: int
		"""
		with await self._lock:
			return len(self.list)

	async def has(self, player):
		"""
		Check if the player is in the queue list.

		:param player: Player object
		:return: boolean
		:rtype: bool
		"""
		with await self._lock:
			return self.list.count(player) != 0

	async def get_position(self, player):
		"""
		Get the position of the player.

		:param player: Player instance
		:return: Integer of the position (index + 1) or None if not found.
		"""
		try:
			with await self._lock:
				return self.list.index(player) + 1
		except ValueError:
			return None

	async def copy(self):
		"""
		Copy the list and return the copy.

		:return: Copy of the player list.
		"""
		with await self._lock:
			return self.list.copy()

	async def pop(self):
		"""
		Get the next player and remove from the queue. Returns None when no next player is available (and the queue is empty).

		:return: Player object or None
		"""
		with await self._lock:
			if len(self.list) > 0:
				player = self.list.pop(0)
			else:
				return None

		# Call change hook.
		if self.change_hook and callable(self.change_hook):
			await self.change_hook(action='pop', entity=player)

		return player

	async def remove(self, player):
		"""
		Remove player from the queue, regardless of the position.

		:param player: Player instance
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: Returns if entry has been removed (bool)
		:rtype: bool
		"""
		with await self._lock:
			try:
				self.list.remove(player)
			except ValueError:
				return False

		# Call change hook.
		if self.change_hook and callable(self.change_hook):
			await self.change_hook(action='remove', entity=player)

		return True

	async def clear(self):
		"""
		Clear and remove everyone from the queue.
		"""
		with await self._lock:
			self.list.clear()

		# Call change hook.
		if self.change_hook and callable(self.change_hook):
			await self.change_hook(action='clear', entity=None)

	async def shuffle(self):
		"""
		Shuffle the queue.
		"""
		with await self._lock:
			shuffle(self.list)

		# Call change hook.
		if self.change_hook and callable(self.change_hook):
			await self.change_hook(action='shuffle', entity=None)
