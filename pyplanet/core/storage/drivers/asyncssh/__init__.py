import asyncssh
import logging
import os
import async_generator
import asyncio_extras

from pyplanet.core.storage import StorageDriver

logger = logging.getLogger(__name__)


class SFTPDriver(StorageDriver):
	"""
	SFTP storage driver is using the asyncssh module to access storage that is situated remotely.

	.. warning::

		This driver is not ready for production use!!

	:option PYPLANET_STORAGE_HOST: Hostname of destinotion server.
	:option PYPLANET_STORAGE_PORT: Port destinotion server.
	:option PYPLANET_STORAGE_USERNAME: Username of the user account.
	:option PYPLANET_STORAGE_PASSWORD: Password of the user account. (optional if you use public/private keys).
	:option PYPLANET_STORAGE_KNOWN_HOSTS: File to the Known Hosts file.
	:option PYPLANET_STORAGE_CLIENT_KEYS: Array with client private keys.
	:option PYPLANET_STORAGE_PASSPHRASE: Passphrase to unlock private key(s).
	"""

	def __init__(self, instance, config):
		super().__init__(instance, config)

		# Extract config to local vars.
		self.host = config.PYPLANET_STORAGE_HOST
		self.port = int(config.PYPLANET_STORAGE_PORT) or 22
		self.username = config.PYPLANET_STORAGE_USERNAME
		self.password = config.PYPLANET_STORAGE_PASSWORD
		self.known_hosts = config.PYPLANET_STORAGE_KNOWN_HOSTS
		self.client_keys = config.PYPLANET_STORAGE_CLIENT_KEYS
		self.passphrase = config.PYPLANET_STORAGE_PASSPHRASE

		self.options = dict(
			host=self.host, port=self.port, known_hosts=self.known_hosts, username=self.username, password=self.password,
			client_keys=self.client_keys, passphrase=self.passphrase,
		)

	@asyncio_extras.async_contextmanager
	async def connect(self):
		ssh = await asyncssh.connect(
			host=self.host, port=self.port, known_hosts=self.known_hosts, username=self.username, password=self.password,
			client_keys=self.client_keys, passphrase=self.passphrase,
		).__aenter__()
		await async_generator.yield_(ssh)
		await ssh.__aexit__()

	@asyncio_extras.async_contextmanager
	async def connect_sftp(self):
		"""
		Get sftp client.

		:return: Sftp client.
		:rtype: asyncssh.SFTPClient
		"""
		ssh = await self.connect().__aenter__()
		sftp = await ssh.start_sftp_client().__aenter__()
		await async_generator.yield_(sftp)
		await sftp.__aexit__()
		await ssh.__aexit__()

	async def chmod(self, path: str, mode: int, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.chmod(self.absolute(path), mode)

	async def chown(self, path: str, uid: int, gid: int, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.chown(self.absolute(path), uid, gid)

	async def close(self, **kwargs):
		pass

	@asyncio_extras.async_contextmanager
	async def open(self, filename: str, mode: str = 'r', **kwargs):
		sftp = await self.connect_sftp().__aenter__()
		fh = await sftp.open(self.absolute(filename), mode, **kwargs).__aenter__()
		await async_generator.yield_(fh)
		await fh.__aexit__()
		await sftp.__aexit__()

	async def get(self, remotepath: str, localpath: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.get(self.absolute(remotepath), localpath, preserve=True, follow_symlinks=True, **kwargs)

	async def put(self, localpath: str, remotepath: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.put(localpath, self.absolute(remotepath), preserve=True, follow_symlinks=True, **kwargs)

	async def listdir(self, path='.', **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.listdir(self.absolute(path))

	async def mkdir(self, path, mode=511, **kwargs):
		async with self.connect_sftp() as sftp:
			attrs = asyncssh.SFTPAttrs()
			attrs.permissions = mode
			for k, v in kwargs.items():
				attrs.__setattr__(k, v)
			await sftp.mkdir(self.absolute(path), attrs)

	async def remove(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.remove(self.absolute(path))

	async def rename(self, oldpath: str, newpath: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.rename(self.absolute(oldpath), self.absolute(newpath))

	async def rmdir(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			async def rm(file):
				if await sftp.isdir(file):
					files = await sftp.listdir(os.path.join(self.absolute(path), file))
					for subfile in files:
						await rm(subfile)
				else:
					await sftp.remove(file)
			await rm(self.absolute(path))

	async def stat(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.stat(self.absolute(path))

	async def symlink(self, source: str, dest: str, **kwargs):
		async with self.connect_sftp() as sftp:
			await sftp.symlink(self.absolute(source), self.absolute(dest))

	async def exists(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.exists(self.absolute(path))

	async def is_file(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.isfile(self.absolute(path))

	async def is_dir(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.isdir(self.absolute(path))

	async def is_link(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			return await sftp.islink(self.absolute(path))

	async def touch(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			async with sftp.open(self.absolute(path), 'w+') as fh:
				await fh.write('')

	def openable(self):
		return True
