import asyncio
import json
import uuid
from xmlrpc.client import dumps

from pyplanet.core.exceptions import TransportException


class Query:
	def __init__(self, client, method, *args, timeout=45, **kwargs):
		"""
		Initiate the prepared query.

		:param client: GbxClient to execute actions.
		:param method: Method name
		:param args: Arguments
		:param timeout: Timeout of the call.
		:type client: pyplanet.core.gbx.client.GbxClient
		:type method: str:
		"""
		self._client = client

		self.packet = None
		self.length = None

		self.method = method
		self.args = args
		self.timeout = timeout
		self.result = None

	async def execute(self):
		"""
		Execute call.

		:return: Future with results.
		:rtype: Future<any>
		"""
		return await self._client.execute(self.method, *self.args, timeout=self.timeout)

	def __await__(self):
		"""
		Execute query directly.
		"""
		return self.execute().__await__()

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
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		self.result = None


class ScriptQuery(Query):

	def __init__(self, client, method, *args, timeout=15, encode_json=True, response_id=True):
		"""
		Initiate a Scripted Query.

		:param client: Client instance
		:param method: Method name
		:param args: Arguments
		:param timeout: Timeout to wait for future result.
		:param encode_json: Is body json? True by default.
		:param response_id: Is request requiring response_id?
		:type client: pyplanet.core.gbx.client.GbxClient
		"""
		# Make sure we call the script stuff with TriggerModeScriptEventArray.
		gbx_method = 'TriggerModeScriptEventArray'
		gbx_args = list()

		# Make sure we generate a response_id.
		if response_id is True:
			self.response_id = uuid.uuid4().hex
		else:
			self.response_id = None

		# Encode to json if args are given, and encode_json is true (default).
		if encode_json and len(args) > 0:
			gbx_args.append(json.dumps(args))
		elif not encode_json and len(args) > 0:
			gbx_args.extend(args)

		# Add the response_id to the end of the argument list.
		if self.response_id:
			gbx_args.append(str(self.response_id))

		super().__init__(client, gbx_method, method, gbx_args, timeout=timeout)

	async def execute(self):
		"""
		Execute call.

		:return: Future with results.
		:rtype: Future<any>
		"""
		# Create new future to be returned. This future will be the answered inside a script callback.
		future = None
		if self.response_id:
			self._client.script_handlers[self.response_id] = future = asyncio.Future()

		# Execute the call itself and register the callback script handler.
		gbx_res = await self._client.execute(self.method, *self.args)

		if self.response_id:
			return await asyncio.wait_for(future, self.timeout) # Timeout after 15 seconds!
		return gbx_res
