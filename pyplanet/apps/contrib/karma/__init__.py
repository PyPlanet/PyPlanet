import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.karma.views import KarmaListView
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting
from pyplanet.apps.core.statistics.models import Score
from pyplanet.apps.core.maniaplanet.models import Player

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.contrib.karma.views import KarmaWidget
from pyplanet.apps.contrib.karma.mxkarma import MXKarma

from .models import Karma as KarmaModel


class Karma(AppConfig):
	name = 'pyplanet.apps.contrib.karma'
	game_dependencies = []
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_votes = []
		self.current_karma = 0.0
		self.current_karma_percentage = 0.0
		self.current_karma_positive = 0.0
		self.current_karma_negative = 0.0
		self.widget = None

		self.setting_expanded_voting = Setting(
			'expanded_voting', 'Expanded voting', Setting.CAT_BEHAVIOUR, type=bool,
			description='Expands the karma voting to use --, -, +-, + and ++.',
			default=False
		)

		self.setting_finishes_before_voting = Setting(
			'finishes_before_voting', 'Finishes before voting', Setting.CAT_BEHAVIOUR, type=int,
			description='Amount of times a player should finish before being allowed to vote.',
			default=0
		)

		self.mx_karma = MXKarma(self)

	async def on_start(self):
		# Register commands.
		await self.instance.command_manager.register(Command(command='whokarma', target=self.show_map_list))

		# Register signals.
		self.context.signals.listen(mp_signals.map.map_begin, self.map_begin)
		self.context.signals.listen(mp_signals.map.map_end, self.mx_karma.map_end)
		self.context.signals.listen(mp_signals.player.player_chat, self.player_chat)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)

		await self.context.setting.register(self.setting_finishes_before_voting, self.setting_expanded_voting)

		# Load initial data.
		await self.get_votes_list(self.instance.map_manager.current_map)
		await self.calculate_karma()
		await self.mx_karma.on_start()

		await self.chat_current_karma()

		self.widget = KarmaWidget(self)
		await self.widget.display()

		await self.load_map_votes()

	async def on_stop(self):
		await self.mx_karma.on_stop()

	async def load_map_votes(self, map=None):
		if map:
			map.karma = await self.get_map_karma(map)
		else:
			maps = {m.id: m for m in self.instance.map_manager.maps}
			map_karmas = dict()

			# Fetch all.
			rows = await KarmaModel.execute(
				KarmaModel.select().where(
					KarmaModel.map_id << list(maps.keys())
				)
			)

			# Group by map.
			for row in rows:
				if row.map_id not in map_karmas:
					map_karmas[row.map_id] = list()
				map_karmas[row.map_id].append(row)

			# Map karma stats.
			for map_id, karma_list in map_karmas.items():
				total_score = 0.0
				for vote in karma_list:
					if vote.expanded_score is not None:
						total_score += vote.expanded_score
					else:
						total_score += vote.score

				maps[map_id].karma = dict(
					vote_count=len(karma_list),
					map_karma=total_score
				)

			del map_karmas
			del maps

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
		await self.mx_karma.map_begin(map)
		await self.chat_current_karma()

		await self.widget.display()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.mx_karma.player_connect(player=player)
		await self.widget.display(player=player)

	async def player_chat(self, player, text, cmd):
		if not cmd:
			if text == '++' or text == '+' or text == '+-' or text == '-+' or text == '-' or text == '--':
				expanded_voting = await self.setting_expanded_voting.get_value()
				if expanded_voting is False:
					if text == '+' or text == '+-' or text == '-+' or text == '-':
						return

				if self.instance.game.game == 'tm':
					finishes_required = await self.setting_finishes_before_voting.get_value()
					player_finishes = await Score.objects.count(Score.select().where(Score.map_id == self.instance.map_manager.current_map.get_id()).where(Score.player_id == player.get_id()))
					if player_finishes < finishes_required:
						message = '$i$f00You have to finish this map at least $fff{}$f00 times before voting!'.format(finishes_required)
						await self.instance.chat(message, player)
						return

				normal_score = -1
				score = -1
				if text == '++':
					normal_score = 1
					score = 1
				elif text == '+':
					normal_score = 1
					score = 0.5
				elif text == '+-' or text == '-+':
					score = 0
				elif text == '-':
					score = -0.5

				player_votes = [x for x in self.current_votes if x.player_id == player.get_id()]
				if len(player_votes) > 0:
					player_vote = player_votes[0]
					if (player_vote.expanded_score is not None and player_vote.expanded_score != score) or \
						(player_vote.expanded_score is None and player_vote.score != score):
						player_vote.score = normal_score
						player_vote.expanded_score = score
						await player_vote.save()

						map = next((m for m in self.instance.map_manager.maps if m.uid == self.instance.map_manager.current_map.uid), None)
						if map is not None:
							map.karma = await self.get_map_karma(self.instance.map_manager.current_map)

						message = '$ff0Successfully changed your karma vote to $fff{}$ff0!'.format(text)
						await self.calculate_karma()
						await asyncio.gather(
							self.instance.chat(message, player),
							self.widget.display()
						)
				else:
					new_vote = KarmaModel(map=self.instance.map_manager.current_map, player=player, score=normal_score, expanded_score=score)
					await new_vote.save()

					self.current_votes.append(new_vote)
					await self.calculate_karma()

					map = next((m for m in self.instance.map_manager.maps if m.uid == self.instance.map_manager.current_map.uid), None)
					if map is not None:
						map.karma = await self.get_map_karma(self.instance.map_manager.current_map)

					message = '$ff0Successfully voted $fff{}$ff0!'.format(text)
					await asyncio.gather(
						self.instance.chat(message, player),
						self.widget.display()
					)

				# Reload map referenced information
				asyncio.ensure_future(self.load_map_votes(map=self.instance.map_manager.current_map))

	async def get_map_karma(self, map):
		vote_list = await KarmaModel.objects.execute(KarmaModel.select().where(KarmaModel.map_id == map.get_id()))

		total_score = 0.0
		for vote in vote_list:
			if vote.expanded_score is not None:
				total_score += vote.expanded_score
			else:
				total_score += vote.score

		return dict(
			vote_count=len(vote_list),
			map_karma=total_score
		)

	async def get_votes_list(self, map):
		vote_list = await KarmaModel.objects.execute(KarmaModel.select(KarmaModel, Player).join(Player).where(KarmaModel.map_id == map.get_id()))
		self.current_votes = list(vote_list)

	async def calculate_karma(self):
		total_score = 0.0
		total_abs = 0.0
		self.current_karma_positive = 0.0
		self.current_karma_negative = 0.0

		for vote in self.current_votes:
			score = vote.score
			if vote.expanded_score is not None:
				score = vote.expanded_score

			total_score += score
			total_abs += abs(score)
			if score > 0:
				self.current_karma_positive += score

		self.current_karma_negative = (total_abs - self.current_karma_positive)
		self.current_karma = total_score
		self.current_karma_percentage = 0
		if self.current_karma_positive > 0:
			self.current_karma_percentage = (self.current_karma_positive / total_abs)

	async def chat_current_karma(self):
		mx_karma = ''
		if self.mx_karma.api.activated:
			mx_karma = ', MX: $fff{}%$ff0 [$fff{}$ff0 votes]'.format(round(self.mx_karma.current_average, 1), self.mx_karma.current_count)

		num_current_votes = len(self.current_votes)
		message = '$ff0Current map karma: $fff{}$ff0 ($fff{}%$ff0) [$fff{}$ff0 votes]{}'.format(
			self.current_karma, round(self.current_karma_percentage * 100, 2), num_current_votes, mx_karma
		)
		await self.instance.chat(message)
