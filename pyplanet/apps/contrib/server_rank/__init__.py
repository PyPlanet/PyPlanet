import logging
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.config import AppConfig
from pyplanet.conf import settings
from pyplanet.contrib.command import Command
from .view import RankListView, RankWidget


class ServerRank(AppConfig):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		db_process = self.instance.process_name
		if settings.DATABASES[db_process]['ENGINE'] == 'peewee_async.MySQLDatabase':
			self.db_type = 'mysql'
		elif settings.DATABASES[db_process]['ENGINE'] == 'peewee_async.PostgresqlDatabase':
			self.db_type = 'postgresql'
		else:
			logging.getLogger(__name__).error('Database type not supported')
			logging.getLogger(__name__).info('Closing down app \'server rank\'')
			self.deactivated = True
			return
		db_name = settings.DATABASES[db_process]['NAME']
		db_ip = settings.DATABASES[db_process]['OPTIONS']['host']
		db_login = settings.DATABASES[db_process]['OPTIONS']['user']
		db_password = settings.DATABASES[db_process]['OPTIONS']['password']

		self.deactivated = False

		try:
			self.engine = sqlalchemy.create_engine(f'{self.db_type}://{db_login}:{db_password}@{db_ip}/{db_name}?charset=utf8mb4',
												   pool_size=10)
		except ModuleNotFoundError as e:
			logging.getLogger(__name__).error('Couldn\'t find module required to communicate with the database!')
			logging.getLogger(__name__).error(e)
			logging.getLogger(__name__).info('Closing down app \'server rank\'')
			self.deactivated = True
		except SQLAlchemyError as e:
			logging.getLogger(__name__).error('Error occurred while starting sql engine.')
			logging.getLogger(__name__).error(e)
			logging.getLogger(__name__).info('Closing down app \'server rank\'')
			self.deactivated = True

		self.text_color = '$f80'
		self.data_color = '$fff'
		self.self_color = '$ff0'

		self.widget = None

	async def on_start(self):
		await self.instance.command_manager.register(
			Command(
				'rank',
				target=self.rank,
				admin=False
			),
			Command(
				'nextrank',
				target=self.next_rank,
				admin=False
			),
			Command(
				'prevrank',
				target=self.prev_rank,
				admin=False
			),
			Command(
				'ranks',
				target=self.ranks,
				admin=False
			)
		)

		self.widget = RankWidget(self)
		await self.update_view()

		self.context.signals.listen(mp_signals.map.map_end, self.update_view)

	async def update_view(self):
		await self.widget.display()


	async def rank(self, player, *args, **kwargs):
		if self.deactivated:
			return

		results = []
		try:
			results = await self.get_rank_data()
		except SQLAlchemyError as e:
			logging.getLogger(__name__).error('SQL error occurred when trying to retrieve server ranks', )
			logging.getLogger(__name__).error(e)
			await self.instance.chat('$f00$iSomething went wrong when trying to calculate your rank. '
									 'Contact the server administrator for more information.', player)
			return

		player_id = player.get_id()
		rank = next(({'index': index, 'avg': x['avg']} for index, x in enumerate(results, 1) if
					 x['id'] == player_id), None)

		# 3 variables for text coloring to keep the format string readable
		tc = self.text_color
		dc = self.data_color
		sc = self.self_color
		if rank:
			await self.instance.chat(f'{tc}Your server rank is: {sc}{rank["index"]}{tc}/{dc}{len(results)}{tc}, '
									 f'avg: {dc}{rank["avg"]}', player)
		else:
			await self.instance.chat(f'{tc}You need at least 1 local record before getting a rank', player)

	async def next_rank(self, player, *args, **kwargs):
		if self.deactivated:
			return

		results = []
		try:
			results = await self.get_rank_data()
		except SQLAlchemyError as e:
			logging.getLogger(__name__).error('SQL error occurred when trying to retrieve server ranks')
			logging.getLogger(__name__).error(e)
			await self.instance.chat('$f00$iSomething went wrong when trying to calculate the next rank. '
									 'Contact the server administrator for more information.', player)
			return

		player_id = player.get_id()
		rank = next(({'index': index, 'sum': int(x['sum']), 'avg': round(float(x['avg']), 1)} for index, x in
					 enumerate(results, 1) if x['id'] == player_id), None)

		# 3 variables for text coloring to keep the format string readable
		tc = self.text_color
		dc = self.data_color
		sc = self.self_color
		if rank:
			if rank['index'] == 1:
				await self.instance.chat(f'{tc}No better ranked player :)', player)
			else:
				next_rank_proxy = results[rank['index'] - 2]
				next_rank = {'index': rank['index'] - 1, 'nickname': next_rank_proxy['nickname'],
							 'sum': int(next_rank_proxy['sum']), 'avg': next_rank_proxy['avg']}
				msg = f'{tc}The next better ranked player is {next_rank["nickname"]}' \
					  f'$z$s{tc} : {sc}{next_rank["index"]}{tc}/' \
					  f'{dc}{len(results)}{tc}, avg: {dc}{next_rank["avg"]}' \
					  f'{tc}, [{dc}-{rank["sum"] - next_rank["sum"]} {tc}RP]: '
				await self.instance.chat(msg, player)
		else:
			await self.instance.chat(f'{tc}You need at least 1 local record before getting a rank', player)

	async def prev_rank(self, player, *args, **kwargs):
		if self.deactivated:
			return

		results = []
		try:
			results = await self.get_rank_data()
		except SQLAlchemyError as e:
			logging.getLogger(__name__).error('SQL error occurred when trying to retrieve server ranks')
			logging.getLogger(__name__).error(e)
			await self.instance.chat('$f00$iSomething went wrong when trying to calculate the previous rank. '
									 'Contact the server administrator for more information.', player)
			return

		player_id = player.get_id()
		rank = next(({'index': index, 'sum': int(x['sum']), 'avg': round(float(x['avg']), 1)} for index, x in
					 enumerate(results, 1) if x['id'] == player_id), None)

		# 3 variables for text coloring to keep the format string readable
		tc = self.text_color
		dc = self.data_color
		sc = self.self_color
		if rank:
			if rank['index'] == len(results):
				await self.instance.chat(f'{tc}No worse ranked player :(', player)
			else:
				prev_rank_proxy = results[rank['index']]
				prev_rank = {'index': rank['index'] + 1, 'nickname': prev_rank_proxy['nickname'],
							 'sum': int(prev_rank_proxy['sum']), 'avg': prev_rank_proxy['avg']}
				msg = f'{tc}The previous worse ranked player is {prev_rank["nickname"]}' \
					  f'$z$s{tc} : {sc}{prev_rank["index"]}{tc}/' \
					  f'{dc}{len(results)}{tc}, avg: {dc}{prev_rank["avg"]}' \
					  f'{tc}, [{dc}+{prev_rank["sum"] - rank["sum"]} {tc}RP]: '
				await self.instance.chat(msg, player)
		else:
			await self.instance.chat(f'{tc}You need at least 1 local record before getting a rank', player)

	async def ranks(self, player, *args, **kwargs):
		if self.deactivated:
			return

		results = []
		try:
			results = await self.get_rank_data()
		except SQLAlchemyError as e:
			logging.getLogger(__name__).error('SQL error occurred when trying to retrieve server ranks')
			logging.getLogger(__name__).error(e)
			await self.instance.chat('$f00$iSomething went wrong when trying to calculate ranks. '
									 'Contact the server administrator for more information.', player)
			return

		if results:
			index = next((index for index, x in enumerate(results, 1) if x['id'] == player.get_id()), len(results))
			data = []
			for i, result in enumerate(results, 1):
				result = dict(result)
				result['index'] = i
				if i == index:
					result['diff'] = '$00f0 RP'
				else:
					diff = int(result['sum'] - results[index - 1]['sum'])
					result['diff'] = (f'$f00{diff}' if i < index else f'$0f0+{diff}') + ' RP'
				data.append(result)
			rank_view = RankListView(self, index, data)
			await rank_view.display(player)

	async def get_rank_data(self):
		maps = self.instance.map_manager.maps
		map_ids = [str(m.get_id()) for m in maps]
		map_ids_sql = '(' + ','.join(map_ids) + ')'
		max_local_records = await (
			await self.instance.setting_manager.get_setting('local_records', 'record_limit')).get_value()

		record_query = {
			'mysql': f'SELECT @rec := CASE WHEN @map_id = map_id THEN @rec + 1 ELSE 1 END AS '
					 f'rec, @map_id := map_id map_id, player_id, score FROM localrecord, '
					 f'(SELECT @map_id := 0, @rec := 0) AS dummy WHERE map_id IN {map_ids_sql} ORDER BY map_id, score',

			'postgres': f'SELECT row_number() over (PARTITION BY map_id ORDER BY score) AS rec, player_id '
						f'FROM localrecord WHERE map_id IN {map_ids_sql} ORDER BY map_id, score'
		}

		decimal_cast_query = {
			'mysql': f'CAST({len(maps)} AS DECIMAL)',
			'postgres': f'{len(maps)}::DECIMAL'
		}

		sum_query = f'(SUM(LEAST(records.rec, {max_local_records})) + ({max_local_records} * ({len(maps)} - COUNT(*))))'

		if self.db_type == 'mysql':
			query = f'SELECT player.id, player.nickname, player.login, {sum_query} AS sum, CAST(({sum_query} / {decimal_cast_query["mysql"]}) AS DECIMAL(5,1)) AS avg ' \
					f'FROM ({record_query["mysql"]}) AS records JOIN player ON player.id = records.player_id GROUP BY player_id ORDER BY sum'
		else:
			query = f'SELECT player.id AS id, player.nickname, player.login, {sum_query} AS sum, ({sum_query} / {decimal_cast_query["postgres"]})::DECIMAL(5,1) AS avg ' \
					f'FROM ({record_query["postgres"]}) AS records JOIN player ON player.id = records.player_id GROUP BY player.id ORDER BY sum'

		# TODO PostGres query needs to be tested for syntax errors

		results = []
		with self.engine.connect() as connection:
			results = connection.execute(query).fetchall()
		return results
