class Vote:
	"""
	Vote object, keeping track of all votes.
	"""

	def __init__(self):
		"""
		Initializes the vote.
		"""
		self.action = ''
		self.requester = None
		self.time_limit = None
		self.votes_required = 0
		self.votes_current = []

		self.vote_added = None
		self.vote_removed = None
		self.vote_passed = None

	async def add_vote(self, player):
		"""
		Called to add a vote by a player to the object.

		:param player: player who voted for the vote
		"""

		if player.login in self.votes_current:
			return False

		self.votes_current.append(player.login)

		await self.fire_added_event(player)
		if len(self.votes_current) >= self.votes_required:
			await self.fire_passed_event()

		return True

	async def remove_vote(self, player):
		"""
		Called to remove a vote by a player to the object.

		:param player: player who against the vote
		"""

		if player.login in self.votes_current:
			self.votes_current.remove(player.login)
			await self.fire_removed_event(player)
			return True

		return False

	async def fire_added_event(self, player):
		"""
		Calls the event for when a vote has been added.

		:param player: player who voted for the vote
		"""

		if self.vote_added is not None:
			await self.vote_added(vote=self, player=player)

	async def fire_removed_event(self, player):
		"""
		Calls the event for when a vote has been removed.

		:param player: player who against the vote
		"""

		if self.vote_removed is not None:
			await self.vote_removed(vote=self, player=player)

	async def fire_passed_event(self, forced=False):
		"""
		Calls the event for when the vote has passed.

		:param forced: whether the vote was forced by the admin
		"""

		if self.vote_passed is not None:
			await self.vote_passed(vote=self, forced=forced)
