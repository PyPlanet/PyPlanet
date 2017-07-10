import asyncio
import logging

from pyplanet.core.gbx.query import Query, ScriptQuery
from pyplanet.utils.functional import empty
from .remote import GbxRemote

logger = logging.getLogger(__name__)


class GbxClient(GbxRemote):
	"""
	The GbxClient implements and extends the GbxRemote (very base) with the initializers, special encoders/decoders,
	some fixes/hacks needed for the gbx protocol and some tweaks. This is all to prevent changes from the core
	most important logic `GbxRemote`.
	"""

	AUTO_RESPONSE_ID = object()
	SUPPORTED_SCRIPT_API_VERSIONS = [
		'2.0.0', '2.1.0', '2.2.0'
	]

	def __init__(self, *args, script_api_version=empty, **kwargs):
		super().__init__(*args, **kwargs)

		self.script_api_version = self.SUPPORTED_SCRIPT_API_VERSIONS[len(self.SUPPORTED_SCRIPT_API_VERSIONS)-1]
		if script_api_version != empty and isinstance(script_api_version, str):
			self.script_api_version = script_api_version

		self.game = self.instance.game
		self.refresh_task = None

	def __call__(self, *args, **kwargs):
		if len(args) <= 0:
			return
		return self.prepare(args[0], *args[1:], **kwargs)

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

		# If we got a list instead. unpack it.
		# if len(queries) == 1 and isinstance(queries[0], collections.Iterable):
		# 	queries = queries[0]

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
		await self('SendHideManialinkPage')

		# Try to get the script api_versions.
		try:
			api_versions = await self('XmlRpc.GetAllApiVersions', timeout=5)
			if 'versions' in api_versions and self.script_api_version in api_versions['versions']:
				await self('XmlRpc.SetApiVersion', self.script_api_version, response_id=False)
			self.script_api_version = await self('XmlRpc.GetApiVersion')
		except Exception as e:
			logger.error('Can\'t set the script API Version! {}'.format(str(e)))

		await self.refresh_info()

		# Schedule refresh every minute!
		self.refresh_task = asyncio.ensure_future(self.__refresh_info_call())

	async def __refresh_info_call(self):
		while True:
			await asyncio.sleep(60)
			await self.refresh_info()

	async def refresh_info(self):
		# Version Information
		res = await self.multicall(
			self('GetVersion'),
			self('GetSystemInfo'),
			self('GameDataDirectory'),
			self('GetMapsDirectory'),
			self('GetSkinsDirectory'),
			self('GetCurrentMapInfo'),
			self('GetServerPassword'),
			self('GetServerPasswordForSpectator'),
			self('GetMaxPlayers'),
			self('GetMaxSpectators'),
			self('GetHideServer'),
			self('GetLadderServerLimits'),
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

		self.game.server_password = res[6]
		self.game.server_spec_password = res[7]
		self.game.server_max_players = res[8]['CurrentValue']
		self.game.server_next_max_players = res[8]['NextValue']
		self.game.server_max_specs = res[9]['CurrentValue']
		self.game.server_next_max_specs = res[9]['NextValue']
		self.game.server_is_private = res[10]

		self.game.ladder_min = res[11]['LadderServerLimitMin']
		self.game.ladder_max = res[11]['LadderServerLimitMax']

		# Detailed server player infos.
		server_player_info = await self('GetDetailedPlayerInfo', self.game.server_player_login)

		self.game.server_language = server_player_info['Language']
		self.game.server_name = server_player_info['NickName']
		self.game.server_path = server_player_info['Path']


async def multicall(*calls):
	"""
	Run the queries given async. Will use one or more multicall(s), depends on content.

	:param queries: Queries to execute in multicall.
	:return: Results in tuple.
	:rtype: tuple<any>
	"""
	from pyplanet.core import Controller
	return await Controller.instance.gbx.multicall(*calls)

