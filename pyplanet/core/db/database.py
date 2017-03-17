"""
The database class in this file holds the engine and state of the database connection. Each instance has one specific
database instance running.
"""
import importlib

import logging
import peewee

from pyplanet.core.exceptions import ImproperlyConfigured
from .registry import Registry

Proxy = peewee.Proxy()


class Database:
	def __init__(self, engine_cls, *args, **kwargs):
		self.engine = engine_cls(*args, **kwargs)
		self.registry = Registry(self)
		Proxy.initialize(self.engine)

	@staticmethod
	def create_from_settings(conf):
		try:
			engine_path, _, cls_name = conf['ENGINE'].rpartition('.')
			db_name = conf['NAME']
			db_options = conf['OPTIONS'] if 'OPTIONS' in conf and conf['OPTIONS'] else dict()

			# We will try to load it so we have the validation inside this class.
			engine = getattr(importlib.import_module(engine_path), cls_name)
		except ImportError:
			raise ImproperlyConfigured('Database engine doesn\'t exist!')
		except Exception as e:
			raise ImproperlyConfigured('Database configuration isn\'t complete or engine could\'t be found!')

		return Database(engine, db_name, **db_options)

	def connect(self):
		self.engine.connect()
		logging.info('Database connection established!')
