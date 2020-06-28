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
