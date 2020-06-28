import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

from pyplanet.apps.config import AppConfig
from pyplanet.conf import settings


class ServerRank(AppConfig):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		db_process = self.instance.process_name
		if settings.DATABASES[db_process]['ENGINE'] == 'peewee_async.MySQLDatabase':
			self.db_type = 'mysql'
		elif settings.DATABASES[db_process]['ENGINE'] == 'peewee_async.PostgresqlDatabase':
			self.db_type = 'postgresql'
		else:
			print('Database type not supported')
			print('Closing down app \'server rank\'')
			self.deactivated = True
			return
		db_name = settings.DATABASES[db_process]['NAME']
		db_ip = settings.DATABASES[db_process]['OPTIONS']['host']
		db_login = settings.DATABASES[db_process]['OPTIONS']['user']
		db_password = settings.DATABASES[db_process]['OPTIONS']['password']

		self.deactivated = False

		try:
			self.engine = sqlalchemy.create_engine(f'{self.db_type}://{db_login}:{db_password}@{db_ip}/{db_name}',
												   pool_size=10)
		except ModuleNotFoundError as e:
			print('Couldn\'t find module required to communicate with the database!')
			print(e)
			print('Closing down app \'server rank\'')
			self.deactivated = True
		except SQLAlchemyError as e:
			print('Error occurred while starting sql engine.')
			print(e)
			print('Closing down app \'server rank\'')
			self.deactivated = True

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
