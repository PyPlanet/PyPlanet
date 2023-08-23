"""
The server information object contains version information about the database server.
"""
import logging
import peewee
from playhouse.sqlite_ext import SqliteExtDatabase

logger = logging.getLogger(__name__)


class ServerInfo:
	def __init__(self, engine, db):
		"""
		Initiate database server information object.

		:param engine: Database engine instance.
		:param db: Database instance.
		"""
		self.engine = engine
		self.db = db
		self.server_type = None
		self.server_version = None
		self.server_version_text = None

	async def determine(self):
		if isinstance(self.db.engine, peewee.SqliteDatabase) or isinstance(self.db.engine, SqliteExtDatabase):
			self.server_type = "sqlite"
			query = "SELECT SQLITE_VERSION() AS version"
		elif isinstance(self.db.engine, peewee.MySQLDatabase):
			self.server_type = "mysql"
			query = "SELECT @@version AS version, @@innodb_version AS innodb_version"
		elif isinstance(self.db.engine, peewee.PostgresqlDatabase):
			self.server_type = "postgresql"
			query = "SHOW SERVER_VERSION"
		else:
			logger.warning("Unable to determine database server version (unknown engine type: {})".format(type(self.db.engine)))
			return

		try:
			cursor = self.engine.execute_sql(query)
			result = cursor.fetchone()

			if result is None or len(result) == 0:
				return

			if self.server_type == "mysql":
				# Use the innodb_version (0) for a clean engine version, use the version (1) as version text.
				self.server_version = result[1]
				self.server_version_text = result[0]

				if "mariadb" in self.server_version_text.lower():
					self.server_type = "mariadb"
			else:
				self.server_version_text = result[0]
				if self.server_type == "postgresql":
					self.server_version = self.server_version_text.split(' ')[0]
				elif self.server_type == "sqlite":
					self.server_version = self.server_version_text

			logger.info("Determined database server type: {}, version: {}".format(self.server_type, self.server_version))
		except:
			# No database version could be established
			logger.warning("Unable to determine database server version (type: {})".format(self.server_type))

