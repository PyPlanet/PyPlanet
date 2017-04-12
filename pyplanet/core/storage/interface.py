
class StorageInterface:
	async def open(self, file: str, mode: str = 'rb'):
		raise NotImplementedError

	async def open_map(self, file: str, mode: str = 'rb'):
		raise NotImplementedError

	async def open_matchsettings(self, file: str, mode: str = 'r'):
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

	async def chmod(self, path: str, mode: int):
		raise NotImplemented

	async def chown(self, path: str, uid: int, gid: int):
		raise NotImplemented

	async def close(self):
		raise NotImplementedError

	async def file(self, filename: str, mode: str = 'r', bufsize=-1):
		raise NotImplementedError

	async def get(self, remotepath: str, localpath: str):
		raise NotImplementedError

	async def getfo(self, remotepath: str, fl):
		raise NotImplementedError

	async def listdir(self, path='.'):
		raise NotImplemented

	async def mkdir(self, path, mode=511):
		raise NotImplemented

	async def put(self, localpath: str, remotepath: str):
		raise NotImplementedError

	async def putfo(self, fl, remotepath: str):
		raise NotImplementedError

	async def remove(self, path: str):
		raise NotImplemented

	async def rename(self, oldpath: str, newpath: str):
		raise NotImplemented

	async def rmdir(self, path: str, recursive=False, force=False):
		raise NotImplemented

	async def stat(self, path: str):
		raise NotImplemented

	async def symlink(self, source: str, dest: str):
		raise NotImplemented


class StorageFile:
	def __init__(self):
		pass

	async def __aenter__(self):
		pass

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		pass

