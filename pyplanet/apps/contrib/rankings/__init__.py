import logging
import math
from peewee import RawQuery

from pyplanet.apps.contrib.rankings.models.ranked_map import RankedMap
from pyplanet.apps.contrib.rankings.models import Rank
from pyplanet.apps.contrib.rankings.views import TopRanksView, MapListView
from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting

logger = logging.getLogger(__name__)


class Rankings(AppConfig):
	# Rankings can only be calculated on Trackmania games.
	game_dependencies = ['trackmania', 'trackmania_next']

	# Rankings depend on the local records.
	app_dependencies = ['core.maniaplanet', 'core.trackmania', 'local_records']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setting_records_required = Setting(
			'minimum_records_required', 'Minimum records to acquire ranking', Setting.CAT_BEHAVIOUR, type=int,
			description='Minimum of records required to acquire a rank (minimum 3 records).',
			default=5
		)

		self.setting_chat_announce = Setting(
			'rank_chat_announce', 'Display server ranks on map start', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether to display the server rank on every map start.',
			default=True
		)

		self.setting_topranks_limit = Setting(
			'topranks_limit', 'Maximum rank to display in topranks', Setting.CAT_BEHAVIOUR, type=int,
			description='Amount of ranks to display in the topranks view.',
			default=100
		)

	async def on_start(self):
		if self.instance.db.engine.__class__.__name__.lower().find('postgresql') != -1:
			raise NotImplementedError("Rankings app only works on PyPlanet instances running on MySQL.")

		# Listen to signals.
		self.context.signals.listen(mp_signals.map.map_end, self.map_end)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)

		# Register commands.
		await self.instance.command_manager.register(
			Command('rank', target=self.chat_rank, description='Displays your current server rank.'),
			Command('nextrank', target=self.chat_nextrank, description='Displays the player ahead of you in the server ranking.'),
			Command('topranks', target=self.chat_topranks, description='Displays a list of top ranked players.'),
		)

		# Register settings
		await self.context.setting.register(self.setting_records_required, self.setting_chat_announce, self.setting_topranks_limit)

	async def map_end(self, map):
		# Calculate server ranks.
		await self.calculate_server_ranks()

		# Display the server rank for all players on the server after calculation, if enabled.
		if await self.setting_chat_announce.get_value():
			for player in self.instance.player_manager.online:
				await self.chat_rank(player)

	async def player_connect(self, player, is_spectator, source, signal):
		if await self.setting_chat_announce.get_value():
			await self.chat_rank(player)

	async def calculate_server_ranks(self):
		maps_on_server = [map_on_server.id for map_on_server in self.instance.map_manager.maps]

		minimum_records_required_setting = await self.setting_records_required.get_value()
		minimum_records_required = minimum_records_required_setting if minimum_records_required_setting >= 3 else 3

		maximum_record_rank = await self.get_maximum_record_rank()

		query = RawQuery(Rank, """
-- Reset the current ranks to insert new ones later one.
TRUNCATE TABLE rankings_rank;
-- Limit on maximum ranked records.
SET @ranked_record_limit = {};
-- Minimum amount of ranked records required to acquire a rank.
SET @minimum_ranked_records = {};
-- Total amount of maps active on the server.
SET @active_map_count = {};
-- Set the rank/current rank variables to ensure correct first calculation
SET @player_rank = 0;
SET @current_rank = 0;
INSERT INTO rankings_rank (player_id, average, calculated_at)
SELECT
	player_id, average, calculated_at
FROM (
	SELECT
		player_id,
		-- Calculation: the sum of the record ranks is combined with the ranked record limit times the amount of unranked maps.
		-- Divide this summed ranking by the amount of active maps on the server, and an average calculated rank will be returned.
		ROUND((SUM(player_rank) + (@active_map_count - COUNT(player_rank)) * @ranked_record_limit) / @active_map_count * 10000, 0) AS average,
		NOW() AS calculated_at,
		COUNT(player_rank) AS ranked_records_count
	FROM
	(
		SELECT
			id,
			map_id,
			player_id,
			score,
			@player_rank := IF(@current_rank = map_id, @player_rank + 1, 1) AS player_rank,
			@current_rank := map_id
		FROM localrecord
		WHERE map_id IN ({})
		ORDER BY map_id, score ASC
	) AS ranked_records
	WHERE player_rank <= @ranked_record_limit
	GROUP BY player_id
) grouped_ranks
WHERE ranked_records_count >= @minimum_ranked_records
		""".format(maximum_record_rank, minimum_records_required, str(len(maps_on_server)), ", ".join(str(map_id) for map_id in maps_on_server)))

		await Rank.execute(query)

	async def chat_topranks(self, player, *args, **kwargs):
		top_ranks_limit = await self.setting_topranks_limit.get_value()
		top_ranks = await Rank.execute(Rank.select(Rank, Player).join(Player).order_by(Rank.average.asc()).limit(top_ranks_limit))
		view = TopRanksView(self, player, top_ranks)
		await view.display(player)

	async def chat_rank(self, player, *args, **kwargs):
		player_rank = await self.get_player_rank(player)
		if player_rank is None:
			await self.instance.chat('$f00$iYou do not have a server rank yet!', player)
			return

		await self.instance.chat('$f80Your server rank is $fff{}$f80 of $fff{}$f80, average: $fff{}$f80'.format(
			player_rank['rank'], player_rank['total_ranked_players'], player_rank['average']), player)

	async def chat_nextrank(self, player, *args, **kwargs):
		player_ranks = await Rank.execute(Rank.select().where(Rank.player == player.get_id()))

		if len(player_ranks) == 0:
			await self.instance.chat('$f00$iYou do not have a server rank yet!', player)
			return

		player_rank = player_ranks[0]
		next_ranked_players = await Rank.execute(
			Rank.select(Rank, Player)
				.join(Player)
				.where(Rank.average < player_rank.average)
				.order_by(Rank.average.desc())
				.limit(1))

		if len(next_ranked_players) == 0:
			await self.instance.chat('$f00$iThere is no better ranked player than you!', player)
			return

		next_ranked = next_ranked_players[0]
		next_player_rank_average = '{:0.2f}'.format((next_ranked.average / 10000))
		next_player_rank_index = (await Rank.objects.count(Rank.select(Rank).where(Rank.average < next_ranked.average)) + 1)
		next_player_rank_difference = math.ceil((player_rank.average - next_ranked.average) / 10000 * len(self.instance.map_manager.maps))

		await self.instance.chat('$f80The next ranked player is $<$fff{}$>$f80 ($fff{}$f80), average: $fff{}$f80 [$fff-{} $f80RP]'.format(
			next_ranked.player.nickname, next_player_rank_index, next_player_rank_average, next_player_rank_difference), player)

	async def chat_norank(self, player, *args, **kwargs):
		ranked_maps = await self.get_player_map_ranks(player)
		non_ranked_maps = [map for map in self.instance.map_manager.maps if
							map.id not in [ranked_map.id for ranked_map in ranked_maps]]

		view = MapListView(self, player, maps=non_ranked_maps, title='Your non-ranked maps on this server', show_rank=False)
		await view.display(player)

	async def chat_bestrank(self, player, *args, **kwargs):
		ranked_maps = await self.get_player_map_ranks(player, 'ORDER BY player_rank ASC')
		view = MapListView(self, player, maps=ranked_maps, title='Your best ranked maps on this server', show_rank=True)
		await view.display(player)

	async def chat_worstrank(self, player, *args, **kwargs):
		ranked_maps = await self.get_player_map_ranks(player, 'ORDER BY player_rank DESC')
		view = MapListView(self, player, maps=ranked_maps, title='Your worst ranked maps on this server', show_rank=True)
		await view.display(player)

	async def get_player_map_ranks(self, player, sort_query = ''):
		maximum_record_rank = await self.get_maximum_record_rank()

		query = '''SELECT
					map.id,
					map.name,
					map.uid,
					map.author_login,
					ranked_records.player_rank
				FROM
				(
					SELECT
						id,
						map_id,
						player_id,
						score,
						@player_rank := IF(@current_rank = map_id, @player_rank + 1, 1) AS player_rank,
						@current_rank := map_id
					FROM localrecord r,
						(SELECT @player_rank := 0) pr,
						(SELECT @current_rank := 0) cr
					ORDER BY map_id, score ASC
				) AS ranked_records

				INNER JOIN map
				ON map.id = map_id

				WHERE player_rank <= {}
				AND player_id = {} {}'''.format(maximum_record_rank, player.id, sort_query)

		select_query = RawQuery(RankedMap, query)
		ranked_maps = [map for map in await RankedMap.execute(select_query) if
					   map.id in [server_map.id for server_map in self.instance.map_manager.maps]]

		return ranked_maps

	async def get_player_rank(self, player):
		player_ranks = await Rank.execute(Rank.select().where(Rank.player == player.get_id()))

		if len(player_ranks) == 0:
			return None

		player_rank = player_ranks[0]
		player_rank_average = '{:0.2f}'.format((player_rank.average / 10000))
		player_rank_index = (await Rank.objects.count(Rank.select(Rank).where(Rank.average < player_rank.average)) + 1)
		total_ranked_players = await Rank.objects.count(Rank.select(Rank))

		return {'rank': player_rank_index, 'average': player_rank_average, 'total_ranked_players': total_ranked_players}

	async def get_maximum_record_rank(self):
		# Determine the maximum record rank that is included in the locals.
		# The rank calculation requires a non-zero value, so if none is provided it'll default to 1000.
		maximum_record_rank = await self.instance.apps.apps['local_records'].setting_record_limit.get_value()
		if maximum_record_rank == 0:
			maximum_record_rank = 1000

		return maximum_record_rank
