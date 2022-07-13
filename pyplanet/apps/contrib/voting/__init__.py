import asyncio
import datetime
import logging

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.contrib.voting.views import VoteWidget
from pyplanet.apps.contrib.voting.vote import Vote
from pyplanet.contrib.command import Command
from pyplanet.contrib.map.exceptions import ModeIncompatible
from pyplanet.contrib.setting import Setting

logger = logging.getLogger(__name__)


class Voting(AppConfig):
	"""
	Chat-based voting plugin.
	"""

	name = 'pyplanet.apps.contrib.voting'
	game_dependencies = ['trackmania', 'trackmania_next', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		"""
		Initializes the voting plugin.
		"""
		super().__init__(*args, **kwargs)

		self.current_vote = None
		self.widget = None
		self.podium_stage = False
		self.extend_current_count = 0

		self.setting_voting_enabled = Setting(
			'voting_enabled', 'Voting enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not chat-based voting is enabled.',
			default=True
		)

		self.setting_voting_ratio = Setting(
			'voting_ratio', 'Voting ratio', Setting.CAT_BEHAVIOUR, type=float,
			description='Ratio of players that have to vote in favour for the vote to go through (between 0 and 1).',
			default=0.6
		)

		self.setting_voting_timeout = Setting(
			'voting_timeout', 'Voting timeout', Setting.CAT_BEHAVIOUR, type=int,
			description='Timeout in seconds before a vote is cancelled if the required votes aren\'t achieved (0 = no timeout).',
			default=120
		)

		self.setting_callvoting_disable = Setting(
			'callvoting_disable', 'Disable callvoting', Setting.CAT_BEHAVIOUR, type=bool,
			description='Disable callvoting when chat-based voting is enabled.',
			default=True
		)

		self.setting_callvoting_timeout = Setting(
			'callvoting_timeout', 'Callvote time-out (chat disabled)', Setting.CAT_BEHAVIOUR, type=int,
			description='Callvote time-out in milliseconds, set when the chat-voting plugin is disabled (0 = disabled).',
			default=60000
		)

		self.setting_enabled_replay = Setting(
			'enabled_replay', 'Replay vote enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not the replay vote is enabled.',
			default=True
		)

		self.setting_enabled_restart = Setting(
			'enabled_restart', 'Restart vote enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not the restart vote is enabled.',
			default=True
		)

		self.setting_enabled_skip = Setting(
			'enabled_skip', 'Skip vote enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not the skip vote is enabled.',
			default=True
		)

		self.setting_enabled_time_extend = Setting(
			'enabled_time_extend', 'Time Extend vote enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not the time extend vote is enabled (only works in TimeAttack mode).',
			default=True
		)

		self.setting_remind_interval = Setting(
			'remind_interval', 'Vote reminder interval', Setting.CAT_BEHAVIOUR, type=int,
			description='Interval in seconds before players are reminded to vote.',
			default=30
		)

		self.setting_extend_max_amount = Setting(
			'extend_max_amount', 'Max number of extends', Setting.CAT_BEHAVIOUR, type=int,
			description='Set max number of extends allowed on map. use -1 for disable.',
			default=-1
		)

	async def on_start(self):
		"""
		Called on starting the application.
		Will register the voting settings, permissions, signals and commands.
		Also creates the voting widget.

		Disables callvoting (server-based voting).
		"""

		await self.context.setting.register(
			self.setting_voting_enabled, self.setting_voting_ratio, self.setting_voting_timeout,
			self.setting_remind_interval, self.setting_enabled_replay, self.setting_enabled_restart,
			self.setting_enabled_skip, self.setting_callvoting_disable, self.setting_callvoting_timeout,
			self.setting_enabled_time_extend, self.setting_extend_max_amount
		)

		await self.instance.permission_manager.register('cancel', 'Cancel the current vote', app=self, min_level=1)
		await self.instance.permission_manager.register('pass', 'Pass the current vote', app=self, min_level=1)

		await self.instance.command_manager.register(
			Command(command='cancel', target=self.cancel_vote, perms='voting:cancel', admin=True,
					description='Cancels the current chat-based vote.'),
			Command(command='pass', target=self.pass_vote, perms='voting:pass', admin=True,
					description='Passes the current chat-based vote.'),
			Command(command='y', aliases=['yes'], target=self.vote_yes,
					description='Votes yes on the current chat-based vote.'),
			Command(command='n', aliases=['no'], target=self.vote_no,
					description='Votes no on the current chat-based vote.'),
			Command(command='replay', target=self.vote_replay,
					description='Starts a chat-based vote to replay the current map.'),
			Command(command='restart', aliases=['res'], target=self.vote_restart,
					description='Starts a chat-based vote to restart the current map.'),
			Command(command='skip', target=self.vote_skip,
					description='Starts a chat-based vote to skip the current map.'),
			Command(command='extend', target=self.vote_extend,
					description='Starts a chat-based vote to extend the playing time on the current map.'),
		)

		self.widget = VoteWidget(self)

		# Register callback.
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)

		if await self.setting_callvoting_disable.get_value() is True:
			# Disable callvoting
			await self.instance.gbx('SetCallVoteTimeOut', 0)

	async def on_stop(self):
		"""
		Called on unloading the application.
		Enables callvoting (server-based voting).
		"""

		timeout = await self.setting_callvoting_timeout.get_value()
		await self.instance.gbx('SetCallVoteTimeOut', timeout)

	async def player_connect(self, player, is_spectator, source, signal):
		"""
		Called on a player connecting to the server.
		Will display the voting widget to the player if a vote is currently running.

		:param player: player that is joining the server
		:param is_spectator: whether the joining player is a spectator
		"""

		if self.widget is None:
			self.widget = VoteWidget(self)

		# If there is currently a vote, display the voting widget.
		if self.current_vote is not None:
			await self.widget.display(player=player)

	async def podium_start(self, **kwargs):
		"""
		Called when the server switches to the podium (when the map is finished).
		Will cancel the current vote is there is one running.
		Also prohibits starting a new vote.
		"""

		self.podium_stage = True
		self.extend_current_count = 0

		if self.current_vote is not None:
			message = '$0cfVote to $fff{}$0cf has been cancelled.'.format(self.current_vote.action)
			await self.instance.chat(message)

			# Hide the voting widget and reset the current vote
			await self.reset_vote()

	async def map_start(self, *args, **kwargs):
		"""
		Called when a new map is being started.
		Enables starting a new vote again.
		"""

		self.podium_stage = False
		self.extend_current_count = 0

	async def cancel_vote(self, player, data, **kwargs):
		"""
		Admin command: //cancel
		Cancels the current vote if there is one running.

		:param player: player (admin) cancelling the vote
		"""

		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		message = '$0cfAdmin $fff{}$z$s$0cf cancelled the current vote to $fff{}$z$s$0cf.'.format(player.nickname,
																								  self.current_vote.action)
		await self.instance.chat(message)

		# Hide the voting widget and reset the current vote
		await self.reset_vote()

	async def pass_vote(self, player, data, **kwargs):
		"""
		Admin command: //pass
		Passes the current vote if there is one running.

		:param player: player (admin) passing the vote
		"""

		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		message = '$0cfAdmin $fff{}$z$s$0cf passed the current vote to $fff{}$z$s$0cf.'.format(player.nickname,
																							   self.current_vote.action)
		await self.instance.chat(message)

		await self.current_vote.fire_passed_event(True)

		# Hide the voting widget and reset the current vote
		await self.reset_vote()

	async def vote_added(self, vote, player):
		"""
		Called when a player voted in favour of the current vote.

		:param vote: current vote
		:param player: player voting for the vote
		"""

		if len(vote.votes_current) >= vote.votes_required:
			message = '$fff{}$z$s$0cf voted to $fff{}$0cf.'.format(player.nickname, vote.action)
			await self.instance.chat(message)
		else:
			required_votes = (vote.votes_required - len(vote.votes_current))
			message = '$fff{}$z$s$0cf voted to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote){}.'.format(
				player.nickname, vote.action, required_votes, ('votes' if required_votes > 1 else 'vote'),
				(' ($fff{}$0cf seconds left)'.format(int(round((
																	   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
			)
			await self.instance.chat(message)

	async def vote_removed(self, vote, player):
		"""
		Called when a player voted against the current vote.

		:param vote: current vote
		:param player: player voting against the vote
		"""

		required_votes = (vote.votes_required - len(vote.votes_current))
		message = '$0cfThere {} $fff{}$0cf more {} needed to $fff{}$0cf (use $fffF5$0cf to vote){}.'.format(
			('are' if required_votes > 1 else 'is'), required_votes, ('votes' if required_votes > 1 else 'vote'),
			vote.action,
			(' ($fff{}$0cf seconds left)'.format(int(round((
																   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
		)
		await self.instance.chat(message)

	async def vote_yes(self, player, data, **kwargs):
		"""
		Chat command: /yes
		Called when a player votes in favour of the vote via the chat.

		:param player: player voting
		"""

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
		else:
			await self.widget.hide(player_logins=[player.login])

	async def vote_no(self, player, data, **kwargs):
		"""
		Chat command: /no
		Called when a player votes against the vote via the chat.

		:param player: player voting
		"""

		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		await self.current_vote.remove_vote(player)
		message = '$0cfYou have successfully voted $fffno$0cf.'
		await self.instance.chat(message, player)

		await self.widget.hide(player_logins=[player.login])

	async def vote_replay(self, player, data, **kwargs):
		"""
		Chat command: /replay
		Called when a player requests to start a replay vote.

		:param player: player requesting the vote
		"""

		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return

		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if await self.setting_voting_enabled.get_value() is False:
			message = '$i$f00Chat-based voting has been disabled via the server settings!'
			await self.instance.chat(message, player)
			return

		if await self.setting_enabled_replay.get_value() is False:
			message = '$i$f00Replay voting has been disabled via the server settings! Try /extend for time-extension of TA-mode'
			await self.instance.chat(message, player)
			return

		if self.podium_stage:
			message = '$i$f00You cannot start a vote during the podium!'
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

		await self.create_vote('replay this map', player, self.vote_replay_passed)

		if 'timeattack' in (await self.instance.mode_manager.get_current_script()).lower() \
			and await self.setting_enabled_time_extend.get_value():
			message = '$i$FD4Did you know that you could also vote for extending the time limit with /extend?'
			await self.instance.chat(message, player)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote){}.'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required,
			('votes' if self.current_vote.votes_required > 1 else 'vote'),
			(' ($fff{}$0cf seconds left)'.format(int(round((
																   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
		)
		await self.instance.chat(message)

		await self.current_vote.add_vote(player)

	async def vote_replay_passed(self, vote, forced):
		"""
		Called when a replay vote gets passed.

		:param vote: vote that passed
		:param forced: whether the vote was forced passed by an admin
		"""

		if 'jukebox' not in self.instance.apps.apps:
			return

		maps_in_jukebox = [j['map'] for j in self.instance.apps.apps['jukebox'].jukebox]
		if self.instance.map_manager.current_map.uid in [m.uid for m in maps_in_jukebox]:
			drop_map = next((item for item in self.instance.apps.apps['jukebox'].jukebox if
							 item['map'].uid == self.instance.map_manager.current_map.uid), None)
			if drop_map is not None:
				self.instance.apps.apps['jukebox'].jukebox.remove(drop_map)

		self.instance.apps.apps['jukebox'].jukebox = [{'player': vote.requester,
													   'map': self.instance.map_manager.current_map}] + \
													 self.instance.apps.apps['jukebox'].jukebox

		if not forced:
			message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)
			await self.instance.chat(message)

		# Hide the voting widget and reset the current vote
		await self.reset_vote()

	async def vote_restart(self, player, data, **kwargs):
		"""
		Chat command: /restart
		Called when a player requests to start a restart vote.

		:param player: player requesting the vote
		"""

		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return

		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if await self.setting_voting_enabled.get_value() is False:
			message = '$i$f00Chat-based voting has been disabled via the server settings!'
			await self.instance.chat(message, player)
			return

		if await self.setting_enabled_restart.get_value() is False:
			message = '$i$f00Restart voting has been disabled via the server settings! Try /extend for time-extension of TA-mode'
			await self.instance.chat(message, player)
			return

		if self.podium_stage:
			message = '$i$f00You cannot start a vote during the podium!'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		await self.create_vote('restart this map', player, self.vote_restart_passed)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote){}.'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required,
			('votes' if self.current_vote.votes_required > 1 else 'vote'),
			(' ($fff{}$0cf seconds left)'.format(int(round((
																   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
		)
		await self.instance.chat(message)

		await self.current_vote.add_vote(player)

	async def vote_restart_passed(self, vote, forced):
		"""
		Called when a restart vote gets passed.

		:param vote: vote that passed
		:param forced: whether the vote was forced passed by an admin
		"""

		message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)

		# Hide the voting widget and reset the current vote
		await self.reset_vote()

		# Dedimania save vreplay/ghost replays first.
		if 'dedimania' in self.instance.apps.apps:
			logger.info('Saving dedimania (v)replays first!..')
			if hasattr(self.instance.apps.apps['dedimania'], 'podium_start'):
				try:
					await self.instance.apps.apps['dedimania'].podium_start()
				except Exception as e:
					logger.exception(e)

		await self.instance.gbx('RestartMap')

		if not forced:
			await self.instance.chat(message)

	async def vote_skip(self, player, data, **kwargs):
		"""
		Chat command: /skip
		Called when a player requests to start a skip vote.

		:param player: player requesting the vote
		"""

		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return

		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if await self.setting_voting_enabled.get_value() is False:
			message = '$i$f00Chat-based voting has been disabled via the server settings!'
			await self.instance.chat(message, player)
			return

		if await self.setting_enabled_skip.get_value() is False:
			message = '$i$f00Skip voting has been disabled via the server settings!'
			await self.instance.chat(message, player)
			return

		if self.podium_stage:
			message = '$i$f00You cannot start a vote during the podium!'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		await self.create_vote('skip this map', player, self.vote_skip_passed)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote){}.'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required,
			('votes' if self.current_vote.votes_required > 1 else 'vote'),
			(' ($fff{}$0cf seconds left)'.format(int(round((
																   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
		)
		await self.instance.chat(message)

		await self.current_vote.add_vote(player)

	async def vote_skip_passed(self, vote, forced):
		"""
		Called when a skip vote gets passed.

		:param vote: vote that passed
		:param forced: whether the vote was forced passed by an admin
		"""

		message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)

		# Hide the voting widget and reset the current vote
		await self.reset_vote()

		await self.instance.gbx('NextMap')

		if not forced:
			await self.instance.chat(message)

	async def vote_extend(self, player, data, **kwargs):
		"""
		Chat command: /extend
		Called when a player requests to start an extend vote.

		:param player: player requesting the vote
		"""

		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return

		extend_max = await self.setting_extend_max_amount.get_value()
		if 0 < extend_max <= self.extend_current_count:
			message = f'$i$f00Map has reached extend limit (max {extend_max})'
			await self.instance.chat(message, player)
			return

		if self.current_vote is not None:
			message = '$i$f00You cannot start a vote while one is already in progress.'
			await self.instance.chat(message, player)
			return

		if await self.setting_voting_enabled.get_value() is False:
			message = '$i$f00Chat-based voting has been disabled via the server settings!'
			await self.instance.chat(message, player)
			return

		if await self.setting_enabled_time_extend.get_value() is False:
			message = '$i$f00Skip voting has been disabled via the server settings!'
			await self.instance.chat(message, player)
			return

		if 'timeattack' not in (await self.instance.mode_manager.get_current_script()).lower():
			message = '$i$f00Time Extend voting is only supported in Time Attack modes!'
			await self.instance.chat(message, player)
			return

		if self.podium_stage:
			message = '$i$f00You cannot start a vote during the podium!'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to vote.'
			await self.instance.chat(message, player)
			return

		await self.create_vote('extend time limit on this map', player, self.vote_extend_passed)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote){}.'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required,
			('votes' if self.current_vote.votes_required > 1 else 'vote'),
			(' ($fff{}$0cf seconds left)'.format(int(round((
																   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
		)
		await self.instance.chat(message)
		await self.current_vote.add_vote(player)

	async def vote_extend_passed(self, vote, forced):
		"""
		Called when an extend vote gets passed.

		:param vote: vote that passed
		:param forced: whether the vote was forced passed by an admin
		"""

		message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)
		self.extend_current_count += 1
		# Hide the voting widget and reset the current vote
		await self.reset_vote()

		try:
			await self.instance.map_manager.extend_ta()
			if not forced:
				await self.instance.chat(message)
		except ModeIncompatible:
			await self.instance.chat('$0cfVote to $fff{}$0cf has failed, current mode not Time Attack?')

	async def vote_reminder(self, vote):
		"""
		Called in a loop to keep informing players via the chat that a vote is open.

		:param vote: vote that is currently open
		"""

		await asyncio.sleep(await self.setting_remind_interval.get_value())

		if self.current_vote is not None:
			required_votes = (self.current_vote.votes_required - len(self.current_vote.votes_current))
			current_required_votes = (vote.votes_required - len(vote.votes_current))
			if self.current_vote.action == vote.action and current_required_votes == required_votes:
				message = '$0cfThere are $fff{}$0cf more {} needed to $fff{}$0cf (use $fffF5$0cf to vote){}.'.format(
					current_required_votes, ('votes' if current_required_votes > 1 else 'vote'),
					self.current_vote.action,
					(' ($fff{}$0cf seconds left)'.format(int(round((
																		   self.current_vote.time_limit - datetime.datetime.now()).total_seconds()))) if self.current_vote.time_limit is not None else '')
				)
				await self.instance.chat(message)

				asyncio.ensure_future(self.vote_reminder(vote))

	async def vote_canceller(self, vote):
		"""
		Called in a loop to keep checking whether the current vote should be cancelled because the time limit is passed.

		:param vote: vote that is currently open
		"""

		await asyncio.sleep(1)

		if self.current_vote is not None and self.current_vote.time_limit is not None:
			if datetime.datetime.now() > self.current_vote.time_limit:
				message = '$0cfVote to $fff{}$0cf has timed out after $fff{}$0cf seconds.'.format(
					self.current_vote.action, await self.setting_voting_timeout.get_value()
				)
				await self.instance.chat(message)

				# Hide the voting widget and reset the current vote
				await self.reset_vote()
			else:
				asyncio.ensure_future(self.vote_canceller(vote))

	async def create_vote(self, action, player, passed_event):
		"""
		Called to create a new current vote.

		:param action: kind of vote that should be created
		:param player: player requesting the vote
		:param passed_event: method to be called when the vote is passed
		"""

		ratio = await self.setting_voting_ratio.get_value()
		players = self.instance.player_manager.count_players

		new_vote = Vote()
		new_vote.action = action
		new_vote.requester = player
		new_vote.votes_current = []
		needed_votes = round(players * ratio)
		if needed_votes > players:
			needed_votes = players
		new_vote.votes_required = needed_votes
		new_vote.vote_added = self.vote_added
		new_vote.vote_removed = self.vote_removed
		new_vote.vote_passed = passed_event

		time_limit = await self.setting_voting_timeout.get_value()
		if time_limit > 0:
			new_vote.time_limit = datetime.datetime.now() + datetime.timedelta(0, time_limit)
			asyncio.ensure_future(self.vote_canceller(new_vote))

		asyncio.ensure_future(self.vote_reminder(new_vote))

		# Set the current vote here, so the widget can access it.
		self.current_vote = new_vote

		# Display the voting widget.
		await self.widget.display()

		# Hide the widget for the vote requester, as that person always votes.
		await self.widget.hide(player_logins=[player.login])

		return new_vote

	async def reset_vote(self):
		"""
		Called to reset the current vote - will hide the widget and reset the variable.
		"""

		await self.widget.hide()
		self.current_vote = None
