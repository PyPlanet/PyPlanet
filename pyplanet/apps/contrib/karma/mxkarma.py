"""
The module and class MXKarma is the communication between the API and the Karma class.
"""
import datetime

from pyplanet.contrib.setting import Setting

from pyplanet.apps.contrib.karma.mxkarmaapi import MXKarmaApi


class MXKarma:
	"""
	The MX Karma sub-app of the Karma app.
	"""

	def __init__(self, app):
		self.app = app
		self.api = MXKarmaApi(self)

		self.current_count = 0
		self.current_average = 0.0
		self.current_start = datetime.datetime.now()
		self.current_votes = None

		self.setting_mx_karma = Setting(
			'mx_karma', 'Enable MX Karma', Setting.CAT_BEHAVIOUR, type=bool,
			description='Enabling MX Karma will provide you with global karma information from ManiaExchange.',
			default=False, change_target=self.reload_settings
		)

		self.setting_mx_karma_key = Setting(
			'mx_karma_key', 'MX Karma API Key', Setting.CAT_BEHAVIOUR, type=str,
			description='Enabling MX Karma will provide you with global karma information from ManiaExchange.',
			default=None, change_target=self.reload_settings
		)

	async def reload_settings(self, *args, **kwargs):
		"""
		Reload the settings from the PyPlanet settings storage and reload/restart the session.

		:param args: args
		:param kwargs: kwargs
		"""
		enabled = await self.setting_mx_karma.get_value()
		key = await self.setting_mx_karma_key.get_value()

		if enabled is True and key is not None:
			await self.api.create_session()
			await self.api.start_session()
		else:
			await self.api.close_session()

	async def determine_vote(self, vote):
		"""
		Convert a local vote to a MX vote value.

		:param vote: vote value of PyPlanet karma app.
		:return: MX Karma vote value
		"""
		mx_vote = 0
		if vote == -0.5:
			mx_vote = 25
		elif vote == 0:
			mx_vote = 50
		elif vote == 0.5:
			mx_vote = 75
		elif vote == 1:
			mx_vote = 100

		return mx_vote

	async def handle_rating(self, rating, importvotes=True):
		"""
		Handle the event of a rating.

		:param rating: Rating dict
		:param importvotes: Import boolean
		:return:
		"""
		if rating is not None:
			self.current_count = rating['votecount']
			self.current_average = rating['voteaverage']
			self.current_votes = rating['votes']

			if not importvotes:
				return

			import_votes = []
			for vote in self.app.current_votes:
				login = vote.player.login
				score = vote.score
				if vote.expanded_score is not None:
					score = vote.expanded_score

				if not any(mx['login'] == login for mx in self.current_votes):
					import_votes.append({'login': login, 'nickname': vote.player.nickname, 'vote': await self.determine_vote(score)})

			if len(import_votes) > 0:
				if await self.api.save_votes(map=self.app.instance.map_manager.current_map, is_import=True, votes=import_votes):
					rating = await self.api.get_map_rating(self.app.instance.map_manager.current_map)
					await self.handle_rating(rating, importvotes=False)

					if len(self.current_votes) != len(import_votes):
						self.current_votes = import_votes
		else:
			self.current_count = 0
			self.current_average = 0.0
			self.current_votes = None

	async def on_start(self):
		"""
		On start of module.
		"""
		await self.app.context.setting.register(
			self.setting_mx_karma, self.setting_mx_karma_key
		)

		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		self.current_start = datetime.datetime.now()

		await self.api.create_session()
		await self.api.start_session()

		rating = await self.api.get_map_rating(self.app.instance.map_manager.current_map)
		await self.handle_rating(rating)

	async def on_stop(self):
		"""
		On stop of module.
		"""
		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		await self.api.close_session()

	async def player_connect(self, player):
		"""
		Get player rating on connection.

		:param player: player instance
		"""
		rating = await self.api.get_map_rating(self.app.instance.map_manager.current_map, player.login)

	async def map_begin(self, map):
		"""
		On map begin, load karma.

		:param map: map instance
		"""
		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		if not self.api.activated:
			return

		self.current_start = datetime.datetime.now()

		rating = await self.api.get_map_rating(map)
		await self.handle_rating(rating)

	async def map_end(self, map):
		"""
		Map end, save votes to API if needed.

		:param map: map instance.
		"""
		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		if not self.api.activated:
			return

		current_map_length = int((datetime.datetime.now() - self.current_start).total_seconds())

		self.current_start = datetime.datetime.now()

		save_votes = []
		for vote in self.app.current_votes:
			login = vote.player.login
			score = vote.score
			if vote.expanded_score is not None:
				score = vote.expanded_score

			player_vote = []
			if self.current_votes is not None:
				player_vote = [v for v in self.current_votes if v['login'] == login]

			new_score = await self.determine_vote(score)
			if len(player_vote) == 0 or (len(player_vote) == 1 and player_vote[0]['vote'] != new_score):
				save_votes.append({'login': login, 'nickname': vote.player.nickname, 'vote': new_score})

		if len(save_votes) > 0:
			await self.api.save_votes(map=self.app.instance.map_manager.current_map, map_length=current_map_length, votes=save_votes)
