import asyncio
import logging

from pyplanet.core.gbx.query import Query, ScriptQuery
from .remote import GbxRemote

logger = logging.getLogger(__name__)


class GbxClient(GbxRemote):
	"""
	The GbxClient implements and extends the GbxRemote (very base) with the initializers, special encoders/decoders,
	some fixes/hacks needed for the gbx protocol and some tweaks. This is all to prevent changes from the core
	most important logic `GbxRemote`.
	"""

	AUTO_RESPONSE_ID = object()

	def __init__(self, *args, script_api_version='2.0.0', **kwargs):
		super().__init__(*args, **kwargs)
		self.script_api_version = script_api_version
		self.game = self.instance.game

	def prepare(self, method, *args, **kwargs):
		"""
		Prepare an query.
		
		:param method: Method name
		:param args: Arguments...
		:return: Prepared query.
		:rtype: pyplanet.core.gbx.query.Query
		"""
		if method not in self.gbx_methods:
			return ScriptQuery(self, method, *args, **kwargs)
		return Query(self, method, *args, **kwargs)

	async def script(self, method, *args, encode_json=True, response_id=True):
		"""
		Execute scripted call.
		
		:param method: Scripted method name
		:param args: Arguments
		:param encode_json: Are the arguments dictionary, should it be encoded? (Then only provide the first arg).
		:param response_id: Does the call work on response_id's?
							True by default, set to false to not expect response with response_id
		:return: Future.
		"""
		query = ScriptQuery(self, method, *args, encode_json=encode_json, response_id=response_id)
		return await query.execute()

	async def multicall(self, *queries):
		"""
		Run the queries given async. Will use one or more multicall(s), depends on content.
		
		:param queries: Queries to execute in multicall.
		:return: Results in tuple.
		:rtype: tuple<any>
		"""
		if len(queries) == 0:
			return tuple()

		# We will try to put the maximum possible calls into one multicall, for this we need to calculate the lengths
		# so we can stay under the maximum allowed package size.
		current_length = 0

		# Current stack holds the current multicall,
		# will be rotated once the multicall reaches the maximum request size.
		current_stack = list()

		# We will stack calls into multicalls. Structure of this list:
		# multicalls = list(   list()   ) = The list contains lists with calls.
		multicalls = list()

		# Create the multicall(s)
		for query in queries:
			if not isinstance(query, Query):
				continue

			query.prepare()
			if current_length + (query.length + 8) < self.MAX_REQUEST_SIZE:
				current_stack.append(query)
				current_length += (query.length + 8)
			else:
				multicalls.append(current_stack)
				current_length = 0
				current_stack = list()

		# Append the last stack.
		if len(current_stack) > 0:
			multicalls.append(current_stack)

		# Create multicall queries.
		calls = list()
		for mc in multicalls:
			calls.append(
				self.execute('system.multicall', [{'methodName': c.method, 'params': c.args} for c in mc])
			)

		multi_results = await asyncio.gather(*calls)
		results = list()
		for res in multi_results:
			if isinstance(res, list) and len(res) > 0 and isinstance(res[0], list):
				# When we have a list inside our list, we will unwrap that to our root results. This is mostly the case,
				# except when we got error messages!
				for row in res:
					results += row
			else:
				results += res

		return results

	async def connect(self):
		await super().connect()
		await self.initialize()
		await self.instance.storage.initialize()

	async def initialize(self):
		"""
		The initialize method will gather information about the server that is only fetched once and saved and used
		in some classes/parts of the application. To make this information available, we use the pyplanet.core.state
		class instance which is a singleton class instance holding information about the server that is public and
		should be stable.
		"""
		# Clear the previous created Manialinks.
		await self.execute('SendHideManialinkPage')

		# Try to get the script api_versions.
		try:
			api_versions = await self.script('XmlRpc.GetAllApiVersions')
			if 'versions' in api_versions and self.script_api_version in api_versions['versions']:
				await self.script('XmlRpc.SetApiVersion', self.script_api_version, response_id=False)
			self.script_api_version = await self.script('XmlRpc.GetApiVersion')
		except Exception as e:
			logger.info('Can\'t set the script API Version! {}'.format(str(e)))

		# Version Information
		res = await self.multicall(
			self.prepare('GetVersion'),
			self.prepare('GetSystemInfo'),
			self.prepare('GameDataDirectory'),
			self.prepare('GetMapsDirectory'),
			self.prepare('GetSkinsDirectory'),
			self.prepare('GetCurrentMapInfo'),
		)
		version_info = res[0]
		self.game.dedicated_version = version_info['Version']
		self.game.dedicated_build = version_info['Build']
		self.game.dedicated_api_version = version_info['ApiVersion']
		self.game.dedicated_title = version_info['TitleId']

		# System Information
		system_info = res[1]
		self.game.server_is_dedicated = system_info['IsDedicated']
		self.game.server_is_server = system_info['IsServer']
		self.game.server_ip = system_info['PublishedIp']
		self.game.server_p2p_port = system_info['P2PPort']
		self.game.server_port = system_info['Port']
		self.game.server_player_login = system_info['ServerLogin']
		self.game.server_player_id = system_info['ServerPlayerId']
		self.game.server_download_rate = system_info['ConnectionDownloadRate']
		self.game.server_upload_rate = system_info['ConnectionUploadRate']

		self.game.server_data_dir = res[2]
		self.game.server_map_dir = res[3]
		self.game.server_skin_dir = res[4]

		self.game.game = self.game.game_from_environment(res[5]['Environnement'])
