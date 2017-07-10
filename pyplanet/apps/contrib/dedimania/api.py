import asyncio
import gzip
import logging
import requests

from xmlrpc.client import dumps, loads

from requests import ConnectTimeout, ReadTimeout

from pyplanet import __version__ as version
from pyplanet.apps.contrib.dedimania.exceptions import DedimaniaTransportException, DedimaniaFault, \
	DedimaniaNotSupportedException, DedimaniaInvalidCredentials
from pyplanet.utils.log import handle_exception

logger = logging.getLogger(__name__)


class DedimaniaAPI:
	API_URL = 'http://dedimania.net:8082/Dedimania'

	def __init__(self, instance, server_login, dedi_code, path, pack_mask, server_version, server_build, game='TM2'):
		"""
		Initiate dedi api.

		:param instance: ControllerInstance
		:param server_login: .
		:param dedi_code: .
		:param path: .
		:param pack_mask: .
		:param server_version: .
		:param server_build: .
		:param game: Game info
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance
		self.loop = instance.loop
		self.client = requests.session()
		self.headers = {
			'User-Agent': 'PyPlanet/{}'.format(version),
			'Accept': 'text/xml',
			'Accept-Encoding': 'gzip',
			'Content-Type': 'text/xml; charset=UTF-8',
			'Content-Encoding': 'gzip',
			'Keep-Alive': 'timeout=600, max=2000',
			'Connection': 'Keep-Alive',
		}

		self.server_login = server_login
		self.dedimania_code = dedi_code
		self.path = path
		self.pack_mask = pack_mask
		self.server_version = server_version
		self.server_build = server_build
		self.game = game

		self.update_task = None
		self.session_id = None
		self.retries = 0

	async def on_start(self):
		pass

	def mode_to_dedi_mode(self, mode):
		mode = mode.lower()
		if mode.startswith('teamattack') or mode.startswith('chase'):
			return False
		elif mode.startswith('rounds') or mode.startswith('team') or mode.startswith('cup'):
			return 'Rounds'
		elif mode.startswith('timeattack') or mode.startswith('laps') or mode.startswith('doppler'):
			return 'TA'
		return False

	def __request(self, body):
		return self.client.request('POST', self.API_URL, None, body, self.headers, timeout=10)

	async def execute(self, method, *args):
		payload = dumps(args, methodname=method, allow_none=True)
		body = gzip.compress(payload.encode('utf8'))
		try:
			res = await self.loop.run_in_executor(None, self.__request, body)
			data, _ = loads(res.text, use_datetime=True)
			if isinstance(data, (tuple, list)) and len(data) > 0 and len(data[0]) > 0:
				if isinstance(data[0][0], dict) and 'faultCode' in data[0][0]:
					raise DedimaniaFault(faultCode=data[0][0]['faultCode'], faultString=data[0][0]['faultString'])
				self.retries = 0
				return data[0]
			raise DedimaniaTransportException('Invalid response from dedimania!')
		except (ConnectionError, ReadTimeout, ConnectionRefusedError) as e:
			raise DedimaniaTransportException(e) from e
		except ConnectTimeout as e:
			raise DedimaniaTransportException(e) from e
		except DedimaniaTransportException:
			# Try to setup new session.
			self.retries += 1
			if self.retries > 5:
				raise DedimaniaTransportException('Dedimania didn\'t gave the right answer after few retries!')
			self.client = requests.session()
			try:
				await self.authenticate()
				return await self.execute(method, *args)
			except Exception as e:
				logger.error('XML-RPC Fault retrieved from Dedimania: {}'.format(str(e)))
				handle_exception(e, __name__, 'execute')
				raise DedimaniaTransportException('Could not retrieve data from dedimania!')
		except DedimaniaFault as e:
			if 'Bad SessionId' in e.faultString or ('SessionId' in e.faultString and 'not found' in e.faultString):
				try:
					self.retries += 1
					if self.retries > 5:
						raise DedimaniaTransportException('Max retries reached for reauthenticating with dedimania!')
					await self.authenticate()
					return await self.execute(method, *args)
				except:
					return
			logger.error('XML-RPC Fault retrieved from Dedimania: {}'.format(str(e)))
			handle_exception(e, __name__, 'execute', extra_data={
				'dedimania_retries': self.retries,
			})
			raise DedimaniaTransportException('Could not retrieve data from dedimania!')

	async def multicall(self, *queries):
		queries = queries + (
			(
				'dedimania.WarningsAndTTR',
			),
		)
		return await self.execute('system.multicall', [{'methodName': c[0], 'params': c[1:]} for c in queries])

	async def authenticate(self):
		try:
			result = await self.multicall(
				('dedimania.OpenSession', {
					'Game': self.game, 'Login': self.server_login, 'Code': self.dedimania_code, 'Path': self.path,
					'Packmask': self.pack_mask, 'ServerVersion': self.server_version, 'ServerBuild': self.server_build,
					'Tool': 'PyPlanet', 'Version': str(version)
				})
			)
		except DedimaniaTransportException as e:
			logger.error('Dedimania Error during authentication: {}'.format(str(e)))
			return
		if not result:
			return

		try:
			if 'Error' in result[0][0] and 'Bad code' in result[0][0]['Error'].lower():
				raise DedimaniaInvalidCredentials('Bad code or login!')
		except DedimaniaInvalidCredentials:
			raise
		except:
			pass

		self.session_id = result[0][0]['SessionId']

		if not self.update_task:
			self.update_task = asyncio.ensure_future(self.update_loop())

		return self.session_id

	async def update_loop(self):
		while True:
			await asyncio.sleep(60 * 4)

			if not self.session_id:
				continue

			def is_spectator(player):
				return bool(player['SpectatorStatus'] % 10)

			players = await self.instance.gbx('GetPlayerList', -1, 0)
			player_list = [
				{'Login': p['Login'], 'IsSpec': is_spectator(p), 'Vote': -1} for p in players if p['Login'] != self.instance.game.server_player_login
			]
			num_specs = sum(p['IsSpec'] for p in player_list)
			num_players = len(player_list) - num_specs
			max_players = self.instance.game.server_max_players['CurrentValue']
			max_specs = self.instance.game.server_max_specs['CurrentValue']
			mode = self.mode_to_dedi_mode(await self.instance.mode_manager.get_current_script())
			if not mode:
				continue
			try:
				response = await self.multicall(
					('dedimania.UpdateServerPlayers', self.session_id, {
						'SrvName': self.instance.game.server_name, 'Comment': '', 'Private': self.instance.game.server_is_private, 'NumPlayers': num_players,
						'MaxPlayers': max_players, 'NumSpecs': num_specs, 'MaxSpecs': max_specs
					}, {
						 'UId': self.instance.map_manager.current_map.uid, 'GameMode': mode,
					 }, player_list)
				)
				assert response[0][0] is True
			except DedimaniaTransportException as e:
				logger.warning('Dedimania update call failed! {}'.format(str(e)))

	async def player_connect(
		self, login, nickname, path, is_spec
	):
		if not self.session_id:
			return None
		try:
			response = await self.multicall(
				('dedimania.PlayerConnect', self.session_id, login, nickname, path, is_spec)
			)
			if not response:
				return None
			response = response[0][0]
			return dict(
				banned=bool(response['Banned']), login=response['Login'], max_rank=response['MaxRank'],
			)
		except DedimaniaTransportException:
			return None

	async def player_disconnect(self, login, tool_option):
		if not self.session_id:
			return True
		await self.multicall(
			('dedimania.PlayerDisconnect', self.session_id, login, tool_option)
		)
		return True

	async def get_map_details(
		self, map, game_mode, server_name, server_comment, is_private, max_players, max_specs, players, server_login
	):
		"""
		Get records for specific map instance.

		:param map: Map instance.
		:param game_mode: Game mode, either 'Rounds' or 'TA'.
		:param server_name: Name of server
		:param server_comment: Comment
		:param is_private: Is server hidden from lists?
		:param max_players: Maximum number of players.
		:param max_specs: Maximum of spectators.
		:param players: List with players, raw from gbx command!!!!!
		:type map: pyplanet.apps.core.maniaplanet.models.map.Map
		:return: Record list.
		"""
		if not self.session_id:
			await self.authenticate()
		if not self.session_id:
			raise DedimaniaTransportException('Dedimania not authenticated!')

		def is_spectator(player):
			return bool(player['SpectatorStatus'] % 10)

		player_list = [
			{'Login': p['Login'], 'IsSpec': is_spectator(p)} for p in players if p['Login'] != server_login
		]
		num_specs = sum(p['IsSpec'] for p in player_list)
		num_players = len(player_list) - num_specs

		mode = self.mode_to_dedi_mode(game_mode)
		if not mode:
			raise DedimaniaNotSupportedException('Mode is not supported!')

		result = await self.multicall(
			('dedimania.GetChallengeRecords', self.session_id, {
				'UId': map.uid, 'Name': map.name, 'Environment': map.environment, 'Author': map.author_login,
				'NbCheckpoints': map.num_checkpoints, 'NbLaps': map.num_laps,
			}, mode, {
				 'SrvName': server_name, 'Comment': server_comment, 'Private': is_private, 'NumPlayers': num_players,
				 'MaxPlayers': max_players, 'NumSpecs': num_specs, 'MaxSpecs': max_specs
			 }, player_list)
		)
		if not result or not isinstance(result, list):
			raise DedimaniaTransportException('Result seems to be empty!')

		result = result[0][0]
		if not result:
			raise DedimaniaTransportException('Result seems to be empty!')

		allowed_modes = result['AllowedGameModes']
		server_max_rank = result['ServerMaxRank']
		response_players = result['Players']
		raw_records = result['Records']
		records = [
			DedimaniaRecord(r['Login'], r['NickName'], r['Best'], r['Rank'], r['MaxRank'], r['Checks'], r['Vote'])
			for r in raw_records
		]
		return server_max_rank, allowed_modes, response_players, records or []

	async def set_map_times(self, map, game_mode, records, v_replay=None, v_replay_checks=None, ghost_replay=None):
		mode = self.mode_to_dedi_mode(game_mode)
		if not mode:
			raise DedimaniaNotSupportedException('Mode is not supported!')

		if not self.session_id:
			raise DedimaniaTransportException('Dedimania not authenticated!')

		times = [{
			'Login': r.login, 'Best': r.score, 'Checks': ','.join([str(c) for c in r.cps]),
		} for r in records if r.updated]
		replays = {
			'VReplay': v_replay or None,
			'VReplayChecks': v_replay_checks or '',
			'Top1GReplay': ghost_replay or ''
		}
		if not replays['VReplay']:
			# Nothing to update!
			logger.debug('Dedimania end map, nothing new to update! Skipping set times call!')
			return

		result = await self.multicall(
			('dedimania.SetChallengeTimes', self.session_id, {
				'UId': map.uid, 'Name': map.name, 'Environment': map.environment, 'Author': map.author_login,
				'NbCheckpoints': map.num_checkpoints, 'NbLaps': map.num_laps,
			}, mode, times, replays)
		)

		try:
			return bool(isinstance(result[0][0]['Records'], list))
		except Exception as e:
			logger.error('Sending times to dedimania failed. Info: {}'.format(result))
			return False


class DedimaniaRecord:

	def __init__(
		self, login, nickname, score, rank, max_rank, cps, vote
	):
		self.login = login
		self.nickname = nickname
		self.score = score
		self.rank = rank
		self.max_rank = max_rank
		self.cps = cps
		self.vote = vote

		self.race_cps = list()

		self.updated = False
		self.new_index = None
