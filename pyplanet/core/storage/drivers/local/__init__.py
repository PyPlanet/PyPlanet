import async_generator
import asyncio_extras
import os
import shutil
import aiofiles

from pyplanet.core.storage import StorageDriver


class LocalDriver(StorageDriver):
	"""
	Local storage driver is using the Python build-in file access utilities for accessing a local storage-like system.
	
	:option BASE_PATH: Override the maniaplanet given base path.
	"""

	def __init__(self, instance, config: dict = None):
		super().__init__(instance, config)

		self.override_base_path = config['BASE_PATH'] if 'BASE_PATH' in config else None

	def absolute(self, path):
		if self.override_base_path:
			return os.path.join(self.override_base_path, path)
		return os.path.join(self.base_dir or '', path)

	async def chmod(self, path: str, mode: int, **kwargs):
		os.chmod(self.absolute(path), mode, **kwargs)

	async def chown(self, path: str, uid: int, gid: int, **kwargs):
		os.chown(self.absolute(path), uid, gid, **kwargs)

	async def close(self, **kwargs):
		pass

	@asyncio_extras.async_contextmanager
	async def open(self, filename: str, mode: str = 'r', **kwargs):
		fh = await aiofiles.open(self.absolute(filename), mode, **kwargs)
		await async_generator.yield_(fh)

	async def get(self, remotepath: str, localpath: str, **kwargs):
		return shutil.copy(src=self.absolute(remotepath), dst=localpath)

	async def put(self, localpath: str, remotepath: str, **kwargs):
		return shutil.copy(src=localpath, dst=self.absolute(remotepath))

	async def listdir(self, path='.', **kwargs):
		return os.listdir(self.absolute(path))

	async def mkdir(self, path, mode=511, **kwargs):
		os.mkdir(self.absolute(path), mode)

	async def remove(self, path: str, **kwargs):
		os.unlink(self.absolute(path), **kwargs)

	async def rename(self, oldpath: str, newpath: str, **kwargs):
		os.rename(self.absolute(oldpath), self.absolute(newpath))

	async def rmdir(self, path: str, **kwargs):
		shutil.rmtree(self.absolute(path), **kwargs)

	async def stat(self, path: str, **kwargs):
		return os.stat(self.absolute(path), **kwargs)

	async def exists(self, path: str, **kwargs):
		return os.path.exists(self.absolute(path))

	async def symlink(self, source: str, dest: str, **kwargs):
		os.symlink(self.absolute(source), self.absolute(dest), **kwargs)

	async def touch(self, path: str, **kwargs):
		async with self.open(path, 'w+') as fh:
			await fh.write('')

	def openable(self):
		return True
