from xmlrpc.client import dumps

from pyplanet.core.exceptions import TransportException


class Query:
	def __init__(self, client, method, *args):
		"""
		Initiate the prepared query.
		:param client: GbxClient to execute actions.
		:param method: Method name
		:param args: Arguments
		:type client: pyplanet.core.gbx.client.GbxClient
		:type method: str:
		"""
		self._client = client

		self.packet = None
		self.length = None

		self.method = method
		self.args = args
		self.result = None

	async def execute(self):
		"""
		Execute call.
		:return: Future with results.
		:rtype: Future<any>
		"""
		return await self._client.execute(self.method, *self.args)

	def prepare(self):
		"""
		Prepare the query, marshall the payload, create binary data and calculate length (size).
		"""
		self.packet = dumps(self.args, methodname=self.method, allow_none=True).encode()
		self.length = len(self.packet)

		if (self.length + 8) > self._client.MAX_REQUEST_SIZE:
			raise TransportException('The prepared query is larger than the maximum request size, we will not send this query!')

	async def __aenter__(self):
		self.result = await self.execute()

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		self.result = None
