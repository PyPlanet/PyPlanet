
class StorageInterface:
	async def open(self, file: str, mode: str = 'rb'):
		raise NotImplementedError

	async def open_map(self, file: str, mode: str = 'rb'):
		raise NotImplementedError

	async def open_match_settings(self, file: str, mode: str = 'r'):
		raise NotImplementedError


class StorageDriver:

	def __init__(self, instance, config: dict = None):
		"""
		Initiate storage driver.
		
		:param instance: Instance instance :P.
		:param config: Driver configuration.
		:type instance: pyplanet.core.instance.Instance
		:type config: dict
		"""
		self.instance = instance
		self.config = config or {}

		self.map_dir = None
		self.skin_dir = None
		self.data_dir = None
		self.base_dir = None

	def absolute(self, path):
		return '{}{}{}'.format(self.base_dir or '', '/' if self.base_dir else '', path)

	async def __aenter__(self, **kwargs):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.close()

	def openable(self):
		raise NotImplementedError

	async def chmod(self, path: str, mode: int, **kwargs):
		raise NotImplemented

	async def chown(self, path: str, uid: int, gid: int, **kwargs):
		raise NotImplemented

	async def close(self, **kwargs):
		raise NotImplementedError

	async def open(self, filename: str, mode: str = 'r', **kwargs):
		raise NotImplemented

	async def get(self, remotepath: str, localpath: str, **kwargs):
		raise NotImplementedError

	async def put(self, localpath: str, remotepath: str, **kwargs):
		raise NotImplementedError

	async def listdir(self, path='.', **kwargs):
		raise NotImplemented

	async def mkdir(self, path, mode=511, **kwargs):
		raise NotImplemented

	async def remove(self, path: str, **kwargs):
		raise NotImplemented

	async def rename(self, oldpath: str, newpath: str, **kwargs):
		raise NotImplemented

	async def rmdir(self, path: str, **kwargs):
		raise NotImplemented

	async def stat(self, path: str, **kwargs):
		raise NotImplemented

	async def exists(self, path: str, **kwargs):
		raise NotImplementedError

	async def symlink(self, source: str, dest: str, **kwargs):
		raise NotImplemented

	async def touch(self, path: str, **kwargs):
		raise NotImplementedError
