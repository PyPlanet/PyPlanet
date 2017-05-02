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
	
	:option HOST: Hostname of destinotion server.
	:option PORT: Port destinotion server.
	:option USERNAME: Username of the user account.
	:option PASSWORD: Password of the user account. (optional if you use public/private keys).
	:option KNOWN_HOSTS: File to the Known Hosts file.
	:option CLIENT_KEYS: Array with client private keys.
	:option PASSPHRASE: Passphrase to unlock private key(s).
	:option KWARGS: Any other options that will be passed to ``asyncssh``.
	"""

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

	async def touch(self, path: str, **kwargs):
		async with self.connect_sftp() as sftp:
			async with sftp.open(self.absolute(path), 'w+') as fh:
				await fh.write('')

	def openable(self):
		return True
