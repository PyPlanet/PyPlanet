import os
import shutil
import aiofiles

from pyplanet.core.storage import StorageDriver


class LocalDriver(StorageDriver):

	async def chmod(self, path: str, mode: int, **kwargs):
		os.chmod(path, mode, **kwargs)

	async def chown(self, path: str, uid: int, gid: int, **kwargs):
		os.chown(path, uid, gid, **kwargs)

	async def close(self, **kwargs):
		pass

	async def open(self, filename: str, mode: str = 'r', **kwargs):
		return await aiofiles.open(filename, mode, **kwargs)

	async def get(self, remotepath: str, localpath: str, **kwargs):
		shutil.copy(src=remotepath, dst=localpath)

	async def put(self, localpath: str, remotepath: str, **kwargs):
		shutil.copy(src=localpath, dst=remotepath)

	async def listdir(self, path='.', **kwargs):
		os.listdir(path)

	async def mkdir(self, path, mode=511, **kwargs):
		os.mkdir(path, mode)

	async def remove(self, path: str, **kwargs):
		os.unlink(path, **kwargs)

	async def rename(self, oldpath: str, newpath: str, **kwargs):
		os.rename(oldpath, newpath)

	async def rmdir(self, path: str, **kwargs):
		shutil.rmtree(path, )

	async def stat(self, path: str, **kwargs):
		os.stat(path, **kwargs)

	async def symlink(self, source: str, dest: str, **kwargs):
		os.symlink(source, dest, **kwargs)

	def openable(self):
		return True
