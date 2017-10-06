class Vote:
	def __init__(self):
		self.action = ''
		self.requester = None
		self.votes_required = 0
		self.votes_current = []

		self.vote_added = None
		self.vote_removed = None
		self.vote_finished = None

	async def add_vote(self, player):
		if player.login in self.votes_current:
			return False

		self.votes_current.append(player.login)

		await self.fire_added_event(player)
		if len(self.votes_current) >= self.votes_required:
			await self.fire_finished_event()

		return True

	async def remove_vote(self, player):
		if player.login in self.votes_current:
			self.votes_current.remove(player.login)
			await self.fire_removed_event(player)
			return True

		return False

	async def fire_added_event(self, player):
		if self.vote_added is not None:
			await self.vote_added(vote=self, player=player)

	async def fire_removed_event(self, player):
		if self.vote_removed is not None:
			await self.vote_removed(vote=self, player=player)

	async def fire_finished_event(self):
		if self.vote_finished is not None:
			await self.vote_finished(vote=self)
