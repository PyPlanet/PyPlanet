import pymysql
import pymysql.cursors


class BaseConverter:
	"""
	Base Converter is the abstract converter class.
	
	Please take a look at the other classes bellow.
	"""
	def __init__(
		self, instance, db_type, db_host, db_name, db_user=None, db_password=None, db_port=None, prefix=None,
		charset='utf8'
	):
		"""
		Create converter.
		
		:param instance: Controller instance.
		:param db_type: Type, mysql by default.
		:param db_host: Hostname
		:param db_name: Name of db schema/database
		:param db_user: Username
		:param db_password: Password
		:param db_port: Port.
		:param prefix: Table prefix.
		:param charset: Charset of source db. Only supporting utf8 now.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance

		self.db_type = db_type
		self.db_host = db_host
		self.db_name = db_name
		self.db_user = db_user
		self.db_password = db_password
		self.db_port = db_port
		self.prefix = prefix or ''
		self.charset = charset

		self.connection = None

	async def connect(self):
		await self.instance.db.connect()
		await self.instance.apps.discover()
		await self.instance.db.initiate()

		if self.db_type != 'mysql':
			raise Exception('We only support mysql converting right now!')

		self.connection = pymysql.connect(
			host=self.db_host, user=self.db_user, password=self.db_password, db=self.db_name, charset=self.charset,
			port=self.db_port or 3306,
			cursorclass=pymysql.cursors.DictCursor
		)

	async def start(self):
		if not self.connection:
			raise Exception('Please connect first (connect()).')
		return await self.migrate(self.connection)

	async def migrate(self, source_connection):
		raise NotImplementedError
