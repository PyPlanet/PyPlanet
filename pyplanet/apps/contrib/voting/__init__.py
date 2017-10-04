import math

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class Voting(AppConfig):
	name = 'pyplanet.apps.contrib.voting'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_vote = None

	async def on_start(self):
		await self.instance.permission_manager.register('cancel', 'Cancel the current vote', app=self, min_level=1)

		await self.instance.command_manager.register(
			Command(command='cancel', target=self.cancel_vote, perms='voting:cancel', admin=True),
			Command(command='y', aliases=['yes'], target=self.vote_yes),
			Command(command='n', aliases=['no'], target=self.vote_no),
			Command(command='replay', target=self.vote_replay),
			Command(command='restart', aliases=['res'], target=self.vote_restart),
			Command(command='skip', target=self.vote_skip),
		)

		# Register callback.
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)

	async def cancel_vote(self, player, data, **kwargs):
		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		self.current_vote = None

		message = '$ff0Admin $fff{}$z$s$ff0 cancelled the current vote.'.format(player.nickname)
		await self.instance.chat(message)

	async def podium_start(self, **kwargs):
		if self.current_vote is not None:
			message = '$ff0Vote to $fff{}$ff0 has been cancelled.'.format(self.current_vote.action)
			await self.instance.chat(message)

			self.current_vote = None

	async def vote_added(self, vote, player):
		if vote.votes_required == len(vote.votes_current):
			message = '$fff{}$z$s$ff0 voted to $fff{}$ff0.'.format(player.nickname, vote.action)
			await self.instance.chat(message)
		else:
			message = '$fff{}$z$s$ff0 voted to $fff{}$ff0, it requires $fff{}$ff0 more votes to pass (use $fff/y$ff0 to vote).'.format(player.nickname, vote.action, (vote.votes_required - len(vote.votes_current)))
			await self.instance.chat(message)

	async def vote_removed(self, vote, player):
		message = '$ff0There are still $fff{}$ff0 more votes needed to pass the vote to $fff{}$ff0 (use $fff/y$ff0 to vote).'.format((vote.votes_required - len(vote.votes_current)), vote.action)
		await self.instance.chat(message)

	async def vote_yes(self, player, data, **kwargs):
		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		if not await self.current_vote.add_vote(player):
			message = '$i$f00You have already voted on this vote!'
			await self.instance.chat(message, player)

	async def vote_no(self, player, data, **kwargs):
		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		await self.current_vote.remove_vote(player)
		message = '$ff0You have successfully voted $fffno$ff0.'
		await self.instance.chat(message, player)

	async def vote_replay(self, player, data, **kwargs):
		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		if 'jukebox' not in self.instance.apps.apps:
			message = '$i$f00The jukebox plugin is required to start a vote to replay this map.'
			await self.instance.chat(message, player)
			return

		if len(self.instance.apps.apps['jukebox'].jukebox) > 0:
			first_juked = self.instance.apps.apps['jukebox'].jukebox[0]
			if first_juked['map'].uid == self.instance.map_manager.current_map.uid:
				message = '$i$f00This map is already being replayed.'
				await self.instance.chat(message, player)
				return

		self.current_vote = self.create_vote('replay this map', player, self.vote_replay_finished)

		message = '$ff0A vote to $fff{}$ff0 was started by $fff{}$z$s$ff0, $fff{}$ff0 votes are required to pass (use $fff/y$ff0 to vote).'.format(self.current_vote.action, player.nickname, self.current_vote.votes_required)
		await self.instance.chat(message)
		await self.current_vote.add_vote(player)

	async def vote_replay_finished(self, vote):
		if 'jukebox' not in self.instance.apps.apps:
			return

		maps_in_jukebox = [j['map'] for j in self.instance.apps.apps['jukebox'].jukebox]
		if self.instance.map_manager.current_map.uid in [m.uid for m in maps_in_jukebox]:
			drop_map = next((item for item in self.instance.apps.apps['jukebox'].jukebox if item['map'].uid == self.instance.map_manager.current_map.uid), None)
			if drop_map is not None:
				self.instance.apps.apps['jukebox'].jukebox.remove(drop_map)

		self.instance.apps.apps['jukebox'].jukebox = [{'player': vote.requester, 'map': self.instance.map_manager.current_map}] + self.instance.apps.apps['jukebox'].jukebox

		message = '$ff0Vote to $fff{}$ff0 has passed.'.format(vote.action)
		await self.instance.chat(message)

		self.current_vote = None

	async def vote_restart(self, player, data, **kwargs):
		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		self.current_vote = self.create_vote('restart this map', player, self.vote_restart_finished)

		message = '$ff0A vote to $fff{}$ff0 was started by $fff{}$z$s$ff0, $fff{}$ff0 votes are required to pass (use $fff/y$ff0 to vote).'.format(self.current_vote.action, player.nickname, self.current_vote.votes_required)
		await self.instance.chat(message)
		await self.current_vote.add_vote(player)

	async def vote_restart_finished(self, vote):
		message = '$ff0Vote to $fff{}$ff0 has passed.'.format(vote.action)

		self.current_vote = None

		await self.instance.gbx.multicall(
			self.instance.gbx('RestartMap'),
			self.instance.chat(message)
		)

	async def vote_skip(self, player, data, **kwargs):
		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		self.current_vote = self.create_vote('skip this map', player, self.vote_skip_finished)

		message = '$ff0A vote to $fff{}$ff0 was started by $fff{}$z$s$ff0, $fff{}$ff0 votes are required to pass (use $fff/y$ff0 to vote).'.format(self.current_vote.action, player.nickname, self.current_vote.votes_required)
		await self.instance.chat(message)
		await self.current_vote.add_vote(player)

	async def vote_skip_finished(self, vote):
		message = '$ff0Vote to $fff{}$ff0 has passed.'.format(vote.action)

		self.current_vote = None

		await self.instance.gbx.multicall(
			self.instance.gbx('NextMap'),
			self.instance.chat(message)
		)

	def create_vote(self, action, player, finished_event):
		vote = Vote()
		vote.action = action
		vote.requester = player
		needed_votes = math.ceil(self.instance.player_manager.count_players / 2)
		if needed_votes == math.floor(self.instance.player_manager.count_players / 2):
			needed_votes += 1
		if needed_votes > self.instance.player_manager.count_players:
			needed_votes = self.instance.player_manager.count_players
		vote.votes_required = needed_votes
		vote.vote_added = self.vote_added
		vote.vote_removed = self.vote_removed
		vote.vote_finished = finished_event

		return vote


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
