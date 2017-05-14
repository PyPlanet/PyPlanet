import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.karma.views import KarmaListView
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting
from pyplanet.apps.core.statistics.models import Score

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.contrib.karma.views import KarmaWidget

from .models import Karma as KarmaModel


class Karma(AppConfig):
	name = 'pyplanet.apps.contrib.karma'
	game_dependencies = []
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_votes = []
		self.current_karma = 0
		self.current_positive_votes = 0
		self.current_negative_votes = 0
		self.widget = None

		self.setting_finishes_before_voting = Setting(
			'finishes_before_voting', 'Finishes before voting', Setting.CAT_BEHAVIOUR, type=int,
			description='Amount of times a player should finish before being allowed to vote.',
			default=0
		)

	async def on_start(self):
		# Register commands.
		await self.instance.command_manager.register(Command(command='whokarma', target=self.show_map_list))

		# Register signals.
		self.instance.signal_manager.listen(mp_signals.map.map_begin, self.map_begin)
		self.instance.signal_manager.listen(mp_signals.player.player_chat, self.player_chat)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)

		await self.context.setting.register(self.setting_finishes_before_voting)

		# Load initial data.
		await self.get_votes_list(self.instance.map_manager.current_map)
		await self.calculate_karma()
		await self.chat_current_karma()

		self.widget = KarmaWidget(self)
		await self.widget.display()

	async def show_map_list(self, player, map=None, **kwargs):
		"""
		Show map list to player for current map or map provided.. Provide player instance.

		:param player: Player instance.
		:param map: Map instance or current map.
		:param kwargs: ...
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: View instance.
		"""
		view = KarmaListView(self, map or self.instance.map_manager.current_map)
		await view.display(player=player.login)
		return view

	async def map_begin(self, map):
		await self.get_votes_list(map)
		await self.calculate_karma()
		await self.chat_current_karma()

		await self.widget.display()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.widget.display(player=player)

	async def player_chat(self, player, text, cmd):
		if not cmd:
			if text == '++' or text == '--':
				if self.instance.game.game == 'tm':
					finishes_required = await self.setting_finishes_before_voting.get_value()
					player_finishes = await Score.objects.count(Score.select().where(Score.map_id == self.instance.map_manager.current_map.get_id()).where(Score.player_id == player.get_id()))
					if player_finishes < finishes_required:
						message = '$i$f00You have to finish this map at least $fff{}$f00 times before voting!'.format(finishes_required)
						await self.instance.chat(message, player)
						return

				score = (1 if text == '++' else -1)
				player_votes = [x for x in self.current_votes if x.player_id == player.get_id()]
				if len(player_votes) > 0:
					player_vote = player_votes[0]
					if player_vote.score != score:
						player_vote.score = score
						await player_vote.save()

						message = '$ff0Successfully changed your karma vote to $fff{}$ff0!'.format(text)
						await self.calculate_karma()
						await asyncio.gather(
							self.instance.chat(message, player),
							self.widget.display()
						)
				else:
					new_vote = KarmaModel(map=self.instance.map_manager.current_map, player=player, score=score)
					await new_vote.save()

					self.current_votes.append(new_vote)
					await self.calculate_karma()

					message = '$ff0Successfully voted $fff{}$ff0!'.format(text)
					await asyncio.gather(
						self.instance.chat(message, player),
						self.widget.display()
					)

	async def get_votes_list(self, map):
		vote_list = await KarmaModel.objects.execute(KarmaModel.select().where(KarmaModel.map_id == map.get_id()))
		self.current_votes = list(vote_list)

	async def calculate_karma(self):
		self.current_positive_votes = [x for x in self.current_votes if x.score == 1]
		self.current_negative_votes = [x for x in self.current_votes if x.score == -1]
		self.current_karma = (len(self.current_positive_votes) - len(self.current_negative_votes))

	async def chat_current_karma(self):
		num_current_votes = len(self.current_votes)
		message = '$ff0Current map karma: $fff{}$ff0 [$fff{}$ff0 votes, ++: $fff{}$ff0 ($fff{}%$ff0), --: $fff{}$ff0 ($fff{}%$ff0)]'.format(
			self.current_karma, num_current_votes,
			len(self.current_positive_votes),
			round((len(self.current_positive_votes) / num_current_votes) * 100, 2) if num_current_votes > 0 else 0,
			len(self.current_negative_votes),
			round((len(self.current_negative_votes) / num_current_votes) * 100, 2) if num_current_votes > 0 else 0,
		)
		await self.instance.chat(message)
