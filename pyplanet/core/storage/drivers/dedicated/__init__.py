from pyplanet.core.storage import StorageDriver


class DedicatedDriver(StorageDriver):
	def get(self, remotepath: str, localpath: str):
		pass

	def putfo(self, fl, remotepath: str):
		pass

	def put(self, localpath: str, remotepath: str):
		pass

	def getfo(self, remotepath: str, fl):
		pass

	def file(self, filename: str, mode: str = 'r', bufsize=-1):
		pass

	def close(self):
		pass
