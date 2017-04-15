import asyncssh
import logging
import os

from pyplanet.core.storage import StorageDriver

logger = logging.getLogger(__name__)


class SFTPDriver(StorageDriver):

	def __init__(self, instance, config: dict = None):
		super().__init__(instance, config)

		# Extract config to local vars.
		self.host = config['HOST']
		self.port = int(config['PORT']) if 'PORT' in config else 22
		self.username = config['USERNAME']
		self.password = config['PASSWORD'] if 'PASSWORD' in config else None
		self.known_hosts = config['KNOWN_HOSTS'] if 'KNOWN_HOSTS' in config and isinstance(config['KNOWN_HOSTS'], list) else []
		self.client_keys = config['CLIENT_KEYS'] if 'CLIENT_KEYS' in config and isinstance(config['CLIENT_KEYS'], list) else []
		self.passphrase = config['PASSPHRASE'] if 'PASSPHRASE' in config else None
		self.kwargs = config['KWARGS'] if 'KWARGS' in config and isinstance(config['KWARGS'], dict) else dict()

	async def connect(self):
		return await asyncssh.connect(
			host=self.host, port=self.port, known_hosts=self.known_hosts, username=self.username, password=self.password,
			client_keys=self.client_keys, passphrase=self.passphrase,
		)

	async def connect_sftp(self):
		"""
		Get sftp client.
		:return: Sftp client.
		:rtype: asyncssh.SFTPClient
		"""
		return await (await self.connect()).start_sftp_client()

	async def chmod(self, path: str, mode: int, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.chmod(path, mode)

	async def chown(self, path: str, uid: int, gid: int, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.chown(path, uid, gid)

	async def close(self, **kwargs):
		pass

	async def open(self, filename: str, mode: str = 'r', **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.open(filename, mode, **kwargs)

	async def get(self, remotepath: str, localpath: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.get(remotepath, localpath, preserve=True, follow_symlinks=True, **kwargs)

	async def put(self, localpath: str, remotepath: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.put(localpath, remotepath, preserve=True, follow_symlinks=True, **kwargs)

	async def listdir(self, path='.', **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.listdir(path)

	async def mkdir(self, path, mode=511, **kwargs):
		async with self.connect_sftp() as sftp:
			attrs = asyncssh.SFTPAttrs()
			attrs.permissions = mode
			for k, v in kwargs.items():
				attrs.__setattr__(k, v)
			await sftp.mkdir(path, attrs)

	async def remove(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.remove(path)

	async def rename(self, oldpath: str, newpath: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.rename(oldpath, newpath)

	async def rmdir(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			async def rm(file):
				if await sftp.isdir(file):
					files = await sftp.listdir(os.path.join(path, file))
					for subfile in files:
						await rm(subfile)
				else:
					await sftp.remove(file)
			await rm(path)

	async def stat(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.stat(path)

	async def symlink(self, source: str, dest: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.symlink(source, dest)

	def openable(self):
		return True
