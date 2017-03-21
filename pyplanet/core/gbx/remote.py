"""
GBXRemote 2 client for python 3.5+ part of PyPlanet.
"""
import asyncio
import logging
import struct
from xmlrpc.client import dumps, loads

from pyplanet import __version__ as version
from pyplanet.core.exceptions import TransportException
from pyplanet.core.events.manager import SignalManager

logger = logging.getLogger(__name__)


class GbxClient:
	"""
	The GbxClient holds the connection to the dedicated server. Maintains the queries and the handlers it got.
	"""

	def __init__(self, host, port, event_pool=None, user=None, password=None, api_version='2013-04-16'):
		"""
		Initiate the GbxRemote client.
		:param host: Host of the dedicated server.
		:param port: Port of the dedicated XML-RPC server.
		:param event_pool: Asyncio pool to execute the handling on.
		:param user: User to authenticate with, in most cases this is 'SuperAdmin'
		:param password: Password to authenticate with.
		:param api_version: API Version to use. In most cases you won't override the default because version changes
							should be abstracted by the other core components.
		:type host: str
		:type port: str int
		:type event_pool: asyncio.BaseEventPool
		:type user: str
		:type password: str
		:type api_version: str
		"""
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.api_version = api_version

		self.event_loop = event_pool or asyncio.get_event_loop()

		self.handlers = dict()
		self.handler_nr = 0x80000000

		self.reader = None
		self.writer = None

	@staticmethod
	def create_from_settings(conf):
		"""
		Create an instance from configuration given for the specific pool
		:param conf: Settings for pool.
		:type conf: dict
		:return: Instance of XML-RPC GbxClient.
		:rtype: GbxClient
		"""
		return GbxClient(
			host=conf['HOST'], port=conf['PORT'], user=conf['USER'], password=conf['PASSWORD']
		)

	async def connect(self):
		"""
		Make connection to the server. This will first check the protocol version and after successful connection
		also authenticate, set the API version and enable callbacks.
		"""
		logger.debug('Trying to connect to the dedicated server...')

		# Create socket (produces coroutine).
		self.reader, self.writer = await asyncio.open_connection(
			host=self.host,
			port=self.port,
			loop=self.event_loop,
		)
		_, header = struct.unpack_from('<L11s', await self.reader.readexactly(15))
		if header.decode() != 'GBXRemote 2':
			raise TransportException('Server is not a valid GBXRemote 2 server.')
		logger.debug('Dedicated connection established!')

		# From now we need to start listening.
		self.event_loop.create_task(self.listen())

		# Startup tasks.
		await self.query('Authenticate', self.user, self.password)
		await asyncio.gather(
			self.query('SetApiVersion', self.api_version),
			self.query('EnableCallbacks', True),
			self.query('ChatSendServerMessage', '$o$w$FD4Py$369Planet$g v{}'.format(version)),
		)

		# Check for scripted mode.
		mode, = await self.query('GetGameMode')
		settings, = await self.query('GetModeScriptSettings')
		if mode == 0 and 'S_UseScriptCallbacks' in settings:
			settings['S_UseScriptCallbacks'] = True
			await self.query('SetModeScriptSettings', settings)

		logger.debug('Dedicated authenticated, API version set and callbacks enabled!')

	async def query(self, method, *args):
		"""
		Query the dedicated server and return the results. This method is a coroutine and should be awaited on.
		The result you get will be a tuple with data inside (the response payload).

		:param method: Server method.
		:param args: Arguments.
		:type method: str
		:type args: tuple
		:return: Tuple with response data (after awaiting).
		:rtype: tuple
		"""
		request_bytes = dumps(args, methodname=method, allow_none=True).encode()
		length_bytes = len(request_bytes).to_bytes(4, byteorder='little')

		handler = self.handler_nr
		if self.handler_nr == 0xffffffff:
			logger.debug('GBX: Reached max handler numbers, RESETTING TO ZERO!')
			self.handler_nr = 0x80000000
		else:
			self.handler_nr += 1

		handler_bytes = handler.to_bytes(4, byteorder='little')

		# Create new future to be returned.
		self.handlers[handler] = future = asyncio.Future()

		# Send to server.
		self.writer.write(length_bytes + handler_bytes + request_bytes)

		return await future

	async def listen(self):
		"""
		Listen to socket.
		"""
		while True:
			head = await self.reader.readexactly(8)
			size, handle = struct.unpack_from('<LL', head)
			body = await self.reader.readexactly(size)
			data, method = loads(body, use_builtin_types=True)

			self.event_loop.create_task(self.handle_payload(handle, method, data))

	async def handle_payload(self, handler_nr, method, data):
		"""
		Handle a callback/response payload.
		:param handler_nr: Handler ID
		:param method: Method name
		:param data: Parsed payload data.
		"""
		if handler_nr in self.handlers:
			logger.debug('GBX: Received response to handler {}'.format(handler_nr))
			handler = self.handlers.pop(handler_nr)
			handler.set_result(data)
			handler.done()
		else:
			logger.debug('GBX: Received callback: {}: {}'.format(method, data))
			signal = SignalManager.get_callback(method)
			if signal:
				results = await signal.send_robust(data)
