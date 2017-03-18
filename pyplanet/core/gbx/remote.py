"""
GBXRemote 2 client for python 3.5+ part of PyPlanet.
"""
import socket
import logging
import asyncio
import threading
import queue
import xml

from xmlrpc.client import loads, dumps, Fault

import time

from pyplanet.core.exceptions import TransportException
from pyplanet.core.events import Manager

logger = logging.getLogger(__name__)


class GbxClient:
	"""
	The GbxClient holds the connection to the dedicated server. Maintains the queries and the handlers it got.
	"""

	def __init__(self, host, port, user=None, password=None, api_version='2013-04-16'):
		"""
		Initiate the GbxRemote client.
		:param host: Host of the dedicated server.
		:param port: Port of the dedicated XML-RPC server.
		:param user: User to authenticate with, in most cases this is 'SuperAdmin'
		:param password: Password to authenticate with.
		:param api_version: API Version to use. In most cases you won't override the default because version changes
							should be abstracted by the other core components.
		:type host: str
		:type port: str int
		:type user: str
		:type password: str
		:type api_version: str
		"""
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.api_version = api_version

		self.handlers = dict()
		self.handler_nr = 0x80000000

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.queue = queue.Queue()
		self.thread = threading.Thread(target=self.listen, daemon=True, name='Gbx')
		self.lock = threading.Lock()

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

		# Set the timeout for connecting...
		self.socket.settimeout(10)
		self.socket.connect((self.host, int(self.port)))

		# Check if we can get a confirmation about the protocol.
		try:
			header_size = int.from_bytes(self.socket.recv(4), byteorder='little')
			header = self.socket.recv(header_size).decode()
			if header != 'GBXRemote 2':
				raise Exception()
		except:
			raise TransportException('Protocol of XML-RPC connection isn\'t a valid GBXRemote 2 protocol!')

		# Reset the timeout, we will keep it open.
		self.socket.settimeout(None)

		logger.debug('Dedicated connection established!')

		# Authenticate, set Api Version and enable callbacks.
		await self.query('Authenticate', self.user, self.password)
		await self.query('SetApiVersion', self.api_version)
		await self.query('EnableCallbacks', True)
		await self.query('ChatSend', '.. Ok ..')
		await self.query('NextMap')

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

		# Upper the handler for the next request.
		self.handler_nr += 1
		handler_bytes = handler.to_bytes(4, byteorder='little')

		future = asyncio.Future()
		self.handlers[handler] = future

		self.socket.send(length_bytes + handler_bytes + request_bytes)
		return future

	def listen(self):
		"""
		Listen for socket activities and call the response handlers or the signal listeners.
		This method should be executed inside of a separate thread!
		.. todo :: Separate thread?
		"""
		self.query('ChatSend', '.. Ok ..')
		while True:
			try:
				size = int.from_bytes(self.socket.recv(4), byteorder='little')
				handler = int.from_bytes(self.socket.recv(4), byteorder='little')
				answer = self.socket.recv(size)

				try:
					with self.lock:
						data, method = loads(answer, use_builtin_types=True)

						if handler in self.handlers:
							logger.debug('XML-RPC: Received response to handler {}'.format(handler))
							self.handlers[handler].set_result(data)
						else:
							logger.debug('XML-RPC: Received callback: {}: {}'.format(method, data))
							signal = Manager.get_callback(method)
							if signal:
								res = signal.send_robust(data)

				except Fault as e:
					logger.exception(e)
				except xml.parsers.expat.ExpatError as e:
					logger.warning('Invalid XML received from XML-RPC connection! {}'.format(str(e)))
				except Exception as e:
					logger.exception(e)

			except OSError as e:
				# Socket closed.
				logger.critical('Socket closed! {}'.format(str(e)))
			except Exception as e:
				logger.exception(e)
			time.sleep(0)
