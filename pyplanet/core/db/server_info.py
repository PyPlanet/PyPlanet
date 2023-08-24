"""
The server information object contains version information about the database server.
"""
import logging
import peewee

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
		self.type = None
		self.version = None
		self.version_text = None

	async def determine(self):
		if isinstance(self.db.engine, peewee.MySQLDatabase):
			self.type = "mysql"
			query = "SELECT @@version AS version"
		elif isinstance(self.db.engine, peewee.PostgresqlDatabase):
			self.type = "postgresql"
			query = "SHOW SERVER_VERSION"
		else:
			logger.warning("Unable to determine database server version (unknown engine type: {})".format(type(self.db.engine)))
			return

		try:
			cursor = self.engine.execute_sql(query)
			result = cursor.fetchone()

			if result is None or len(result) == 0:
				return

			if self.type == "mysql":
				# Use the innodb_version (1) for a clean engine version, use the version (0) as version text.
				self.version_text = result[0]
				self.version = self.version_text.split('-')[0]

				if "mariadb" in self.version_text.lower():
					self.type = "mariadb"
			elif self.type == "postgresql":
				self.version_text = result[0]
				self.version = self.version_text.split(' ')[0]

			logger.info("Determined database server type: {}, version: {}".format(self.type, self.version))
		except:
			# No database version could be established
			logger.warning("Unable to determine database server version (type: {})".format(self.type))

