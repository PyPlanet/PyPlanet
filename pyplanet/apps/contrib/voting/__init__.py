import asyncio
import logging
import math

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.contrib.voting.views import VoteWidget
from pyplanet.apps.contrib.voting.vote import Vote
from pyplanet.contrib.command import Command
from pyplanet.contrib.map.exceptions import ModeIncompatible
from pyplanet.contrib.setting import Setting

logger = logging.getLogger(__name__)


class Voting(AppConfig):
	name = 'pyplanet.apps.contrib.voting'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_vote = None
		self.widget = None
		self.podium_stage = False

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

	async def on_start(self):
		await self.context.setting.register(
			self.setting_voting_enabled, self.setting_voting_ratio, self.setting_remind_interval, self.setting_enabled_replay,
			self.setting_enabled_restart, self.setting_enabled_skip, self.setting_callvoting_disable,
			self.setting_callvoting_timeout, self.setting_enabled_time_extend
		)

		await self.instance.permission_manager.register('cancel', 'Cancel the current vote', app=self, min_level=1)
		await self.instance.permission_manager.register('pass', 'Pass the current vote', app=self, min_level=1)

		await self.instance.command_manager.register(
			Command(command='cancel', target=self.cancel_vote, perms='voting:cancel', admin=True),
			Command(command='pass', target=self.pass_vote, perms='voting:pass', admin=True),
			Command(command='y', aliases=['yes'], target=self.vote_yes),
			Command(command='n', aliases=['no'], target=self.vote_no),
			Command(command='replay', target=self.vote_replay),
			Command(command='restart', aliases=['res'], target=self.vote_restart),
			Command(command='skip', target=self.vote_skip),
			Command(command='extend', target=self.vote_extend),
		)

		self.widget = VoteWidget(self)
		await self.widget.display()

		# Register callback.
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)

		if await self.setting_callvoting_disable.get_value() is True:
			# Disable callvoting
			await self.instance.gbx('SetCallVoteTimeOut', 0)

	async def on_stop(self):
		# Enable callvoting again on unloading the plugin.
		timeout = await self.setting_callvoting_timeout.get_value()
		await self.instance.gbx('SetCallVoteTimeOut', timeout)

	async def player_connect(self, player, is_spectator, source, signal):
		if self.widget is None:
			self.widget = VoteWidget(self)

		await self.widget.display(player=player)

	async def podium_start(self, **kwargs):
		self.podium_stage = True

		if self.current_vote is not None:
			message = '$0cfVote to $fff{}$0cf has been cancelled.'.format(self.current_vote.action)
			await self.instance.chat(message)

			self.current_vote = None

	async def map_start(self, *args, **kwargs):
		self.podium_stage = False

	async def cancel_vote(self, player, data, **kwargs):
		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		message = '$0cfAdmin $fff{}$z$s$0cf cancelled the current vote to $fff{}$z$s$0cf.'.format(player.nickname, self.current_vote.action)
		await self.instance.chat(message)

		self.current_vote = None

	async def pass_vote(self, player, data, **kwargs):
		if self.current_vote is None:
			message = '$i$f00There is currently no vote in progress.'
			await self.instance.chat(message, player)
			return

		message = '$0cfAdmin $fff{}$z$s$0cf passed the current vote to $fff{}$z$s$0cf.'.format(player.nickname, self.current_vote.action)
		await self.instance.chat(message)

		await self.current_vote.fire_finished_event(True)

		self.current_vote = None

	async def vote_added(self, vote, player):
		if len(vote.votes_current) >= vote.votes_required:
			message = '$fff{}$z$s$0cf voted to $fff{}$0cf.'.format(player.nickname, vote.action)
			await self.instance.chat(message)
		else:
			required_votes = (vote.votes_required - len(vote.votes_current))
			message = '$fff{}$z$s$0cf voted to $fff{}$0cf, $fff{}$0cf more {} are needed (use $fffF5$0cf to vote).'.format(
				player.nickname, vote.action, required_votes, ('votes' if required_votes > 1 else 'vote')
			)
			await self.instance.chat(message)

	async def vote_removed(self, vote, player):
		required_votes = (vote.votes_required - len(vote.votes_current))
		message = '$0cfThere are $fff{}$0cf more {} needed to $fff{}$0cf (use $fffF5$0cf to vote).'.format(
			required_votes, ('votes' if required_votes > 1 else 'vote'), vote.action
		)
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
		message = '$0cfYou have successfully voted $fffno$0cf.'
		await self.instance.chat(message, player)

	async def vote_replay(self, player, data, **kwargs):
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

		self.current_vote = await self.create_vote('replay this map', player, self.vote_replay_finished)

		if 'timeattack' in (await self.instance.mode_manager.get_current_script()).lower() \
			and await self.setting_enabled_time_extend.get_value():
			message = '$i$FD4Did you know that you could also vote for extending the time limit with /extend?'
			await self.instance.chat(message, player)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote).'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required, ('votes' if self.current_vote.votes_required > 1 else 'vote')
		)
		await self.instance.chat(message)

		await self.current_vote.add_vote(player)

	async def vote_replay_finished(self, vote, forced):
		if 'jukebox' not in self.instance.apps.apps:
			return

		maps_in_jukebox = [j['map'] for j in self.instance.apps.apps['jukebox'].jukebox]
		if self.instance.map_manager.current_map.uid in [m.uid for m in maps_in_jukebox]:
			drop_map = next((item for item in self.instance.apps.apps['jukebox'].jukebox if item['map'].uid == self.instance.map_manager.current_map.uid), None)
			if drop_map is not None:
				self.instance.apps.apps['jukebox'].jukebox.remove(drop_map)

		self.instance.apps.apps['jukebox'].jukebox = [{'player': vote.requester, 'map': self.instance.map_manager.current_map}] + self.instance.apps.apps['jukebox'].jukebox

		if not forced:
			message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)
			await self.instance.chat(message)

		self.current_vote = None

	async def vote_restart(self, player, data, **kwargs):
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

		self.current_vote = await self.create_vote('restart this map', player, self.vote_restart_finished)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote).'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required, ('votes' if self.current_vote.votes_required > 1 else 'vote')
		)
		await self.instance.chat(message)

		await self.current_vote.add_vote(player)

	async def vote_restart_finished(self, vote, forced):
		message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)

		self.current_vote = None

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

		self.current_vote = await self.create_vote('skip this map', player, self.vote_skip_finished)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote).'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required, ('votes' if self.current_vote.votes_required > 1 else 'vote')
		)
		await self.instance.chat(message)

		await self.current_vote.add_vote(player)

	async def vote_skip_finished(self, vote, forced):
		message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)

		self.current_vote = None

		await self.instance.gbx('NextMap')

		if not forced:
			await self.instance.chat(message)

	async def vote_extend(self, player, data, **kwargs):
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

		self.current_vote = await self.create_vote('extend time limit on this map', player, self.vote_extend_finished)

		message = '$fff{}$z$s$0cf wants to $fff{}$0cf, $fff{}$0cf more {} needed (use $fffF5$0cf to vote).'.format(
			player.nickname, self.current_vote.action, self.current_vote.votes_required, ('votes' if self.current_vote.votes_required > 1 else 'vote')
		)
		await self.instance.chat(message)
		await self.current_vote.add_vote(player)

	async def vote_extend_finished(self, vote, forced):
		message = '$0cfVote to $fff{}$0cf has passed.'.format(vote.action)
		self.current_vote = None

		try:
			await self.instance.map_manager.extend_ta()
			if not forced:
				await self.instance.chat(message)
		except ModeIncompatible:
			await self.instance.chat('$0cfVote to $fff{}$0cf has failed, current mode not Time Attack?')

	async def vote_reminder(self, vote):
		await asyncio.sleep(await self.setting_remind_interval.get_value())

		if self.current_vote is not None:
			required_votes = (self.current_vote.votes_required - len(self.current_vote.votes_current))
			current_required_votes = (vote.votes_required - len(vote.votes_current))
			if self.current_vote.action == vote.action and current_required_votes == required_votes:
				message = '$0cfThere are $fff{}$0cf more {} needed to $fff{}$0cf (use $fffF5$0cf to vote).'.format(
					current_required_votes, ('votes' if current_required_votes > 1 else 'vote'), self.current_vote.action
				)
				await self.instance.chat(message)

				asyncio.ensure_future(self.vote_reminder(vote))

	async def create_vote(self, action, player, finished_event):
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
		new_vote.vote_finished = finished_event

		asyncio.ensure_future(self.vote_reminder(new_vote))

		return new_vote
