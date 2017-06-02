"""
The database class in this file holds the engine and state of the database connection. Each instance has one specific
database instance running.
"""
import contextlib
import importlib
import logging
import peewee
import peewee_async

from pyplanet.core.exceptions import ImproperlyConfigured
from .registry import Registry
from .migrator import Migrator

Proxy = peewee.Proxy()


class Database:
	def __init__(self, engine_cls, instance, *args, **kwargs):
		"""
		Initiate database.

		:param engine_cls: Engine class
		:param instance: Instance of the app.
		:param args: *
		:param kwargs: **
		:type instance: pyplanet.core.instance.Instance
		"""
		self.engine = engine_cls(*args, **kwargs)
		self.instance = instance
		self.migrator = Migrator(self.instance, self)
		self.registry = Registry(self.instance, self)
		self.objects = peewee_async.Manager(self.engine, loop=self.instance.loop)

		# Don't allow any sync code.
		if hasattr(self.engine, 'allow_sync'):
			self.engine.allow_sync = False

		Proxy.initialize(self.engine)

	@classmethod
	def create_from_settings(cls, instance, conf):
		try:
			engine_path, _, cls_name = conf['ENGINE'].rpartition('.')
			db_name = conf['NAME']
			db_options = conf['OPTIONS'] if 'OPTIONS' in conf and conf['OPTIONS'] else dict()

			# FIX for #331. Replace utf8 by utf8mb4 in the mysql driver encoding.
			if conf['ENGINE'] == 'peewee_async.MySQLDatabase' and 'charset' in db_options and db_options['charset'] == 'utf8':
				logging.info('Forcing to use \'utf8mb4\' instead of \'utf8\' for the MySQL charset option! (Fix #331).')
				db_options['charset'] = 'utf8mb4'

			# We will try to load it so we have the validation inside this class.
			engine = getattr(importlib.import_module(engine_path), cls_name)
		except ImportError:
			raise ImproperlyConfigured('Database engine doesn\'t exist!')
		except Exception as e:
			raise ImproperlyConfigured('Database configuration isn\'t complete or engine could\'t be found!')

		return cls(engine, instance, db_name, **db_options)

	@contextlib.contextmanager
	def __fake_allow_sync(self):
		try:
			yield
		except:
			raise

	def allow_sync(self, *args, **kwargs):
		"""
		Wrapper around engine allow_sync to allow failover when no async driver.

		:param args:
		:param kwargs:
		:return:
		"""
		if hasattr(self.engine, 'allow_sync'):
			return self.engine.allow_sync()
		return self.__fake_allow_sync()

	async def connect(self):
		self.engine.connect()
		logging.info('Database connection established!')

	async def initiate(self):
		# Create the migration table.
		from .models import migration
		with self.allow_sync():
			migration.Migration.create_table(True)

		# Execute checks.
		with self.allow_sync():
			await self.migrator.check()

		# Migrate all models.
		with self.allow_sync():
			await self.migrator.migrate()

	async def drop_tables(self):
		from .models import migration
		with self.allow_sync():
			try:
				migration.Migration.drop_table(True, True)
			except:
				pass

			restart = 0
			while restart < 5:
				for name, (_, _, model) in self.registry.models.items():
					try:
						model.drop_table(True, True)
					except:
						restart += 1
