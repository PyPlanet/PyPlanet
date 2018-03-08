"""
The list module contains the class to hold all the queued players.
"""

import asyncio

from pyplanet.apps.contrib.queue.exception import PlayerAlreadyInQueue


class QueueList:
	"""
	The Queue List holds the actual queue and manages it's list thread-safe.
	"""

	def __init__(self):
		self.list = list()
		self._lock = asyncio.Lock()
		self.lock = asyncio.Lock()

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
			return index

	async def count(self):
		"""
		Get the current count of the queue.

		:return: Count of list.
		:rtype: int
		"""
		with await self._lock:
			return len(self.list)

	async def pop(self):
		"""
		Get the next player and remove from the queue. Returns None when no next player is available (and the queue is empty).

		:return: Player object or None
		"""
		with await self._lock:
			if len(self.list) > 0:
				return self.list.pop(0)
			return None

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
			return True

	async def clear(self):
		"""
		Clear and remove everyone from the queue.
		"""
		with await self._lock:
			self.list.clear()
