import asyncio
import gzip
import logging
import requests

from pprint import pprint
from xmlrpc.client import dumps, loads

from pyplanet import __version__ as version

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

	async def on_start(self):
		pass

	async def execute(self, method, *args):
		payload = dumps(args, methodname=method, allow_none=True)
		body = gzip.compress(payload.encode('utf8'))
		res = await self.loop.run_in_executor(None, self.client.request, 'POST', self.API_URL, None, body, self.headers)
		return loads(res.text, use_datetime=True)[0]

	async def multicall(self, *queries):
		queries = queries + (
			(
				'dedimania.WarningsAndTTR',
			),
		)
		return await self.execute('system.multicall', [{'methodName': c[0], 'params': c[1:]} for c in queries])

	async def authenticate(self):
		result = await self.multicall(
			('dedimania.OpenSession', {
				'Game': self.game, 'Login': self.server_login, 'Code': self.dedimania_code, 'Path': self.path,
				'Packmask': self.pack_mask, 'ServerVersion': self.server_version, 'ServerBuild': self.server_build,
				'Tool': 'PyPlanet', 'Version': str(version)
			})
		)
		self.session_id = result[0][0][0]['SessionId']

		if not self.update_task:
			self.update_task = asyncio.ensure_future(self.update_loop())

		return self.session_id

	async def update_loop(self):
		while True:
			await asyncio.sleep(60 * 4)

			def is_spectator(player):
				return bool(player['SpectatorStatus'] % 10)

			players = await self.instance.gbx.execute('GetPlayerList', -1, 0)
			player_list = [
				{'Login': p['Login'], 'IsSpec': is_spectator(p), 'Vote': -1} for p in players if p['Login'] != self.instance.game.server_player_login
			]
			num_specs = sum(p['IsSpec'] for p in player_list)
			num_players = len(player_list) - num_specs
			max_players = self.instance.game.server_max_players['CurrentValue']
			max_specs = self.instance.game.server_max_specs['CurrentValue']
			mode = 'TA' if 'TimeAttack' in await self.instance.mode_manager.get_current_script() else 'Rounds',
			try:
				response = await self.multicall(
					('dedimania.UpdateServerPlayers', self.session_id, {
						'SrvName': self.instance.game.server_name, 'Comment': '', 'Private': self.instance.game.server_is_private, 'NumPlayers': num_players,
						'MaxPlayers': max_players, 'NumSpecs': num_specs, 'MaxSpecs': max_specs
					}, {
						'UId': self.instance.map_manager.current_map.uid, 'GameMode': mode,
					}, player_list)
				)
				assert response[0][0][0] is True
			except:
				logger.warning('Dedimania update call failed!')

	async def player_connect(
		self, login, nickname, path, is_spec
	):
		response = await self.multicall(
			('dedimania.PlayerConnect', self.session_id, login, nickname, path, is_spec)
		)
		response = response[0][0][0]
		return dict(
			banned=bool(response['Banned']), login=response['Login'], max_rank=response['MaxRank'],
		)

	async def player_disconnect(self, login, tool_option):
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

		def is_spectator(player):
			return bool(player['SpectatorStatus'] % 10)

		player_list = [
			{'Login': p['Login'], 'IsSpec': is_spectator(p)} for p in players if p['Login'] != server_login
		]
		num_specs = sum(p['IsSpec'] for p in player_list)
		num_players = len(player_list) - num_specs

		result = await self.multicall(
			('dedimania.GetChallengeRecords', self.session_id, {
				'UId': map.uid, 'Name': map.name, 'Environment': map.environment, 'Author': map.author_login,
				'NbCheckpoints': map.num_checkpoints, 'NbLaps': map.num_laps,
			}, game_mode, {
				'SrvName': server_name, 'Comment': server_comment, 'Private': is_private, 'NumPlayers': num_players,
				'MaxPlayers': max_players, 'NumSpecs': num_specs, 'MaxSpecs': max_specs
			}, player_list)
		)
		result = result[0][0][0]
		allowed_modes = result['AllowedGameModes']
		server_max_rank = result['ServerMaxRank']
		response_players = result['Players']
		raw_records = result['Records']
		records = [
			DedimaniaRecord(r['Login'], r['NickName'], r['Best'], r['Rank'], r['MaxRank'], r['Checks'], r['Vote'])
			for r in raw_records
		]
		return server_max_rank, allowed_modes, response_players, records or []

	async def set_map_times(self, map, game_mode, records):
		times = [{
			'Login': r.login, 'Best': r.score, 'Checks': ','.join([str(c) for c in r.cps]),
		} for r in records if r.virtual_replay]
		replays = {
			'VReplay': None, 'VReplayChecks': '', 'Top1GReplay': ''
		}
		for idx, record in enumerate(records):
			if not replays['VReplay'] and record.virtual_replay:
				replays['VReplay'] = record.virtual_replay
			if not replays['Top1GReplay'] and idx == 0 and record.ghost_replay:
				replays['Top1GReplay'] = record.ghost_replay

		if not replays['VReplay']:
			# Nothing to update!
			logger.debug('Dedimania end map, nothing new to update! Skipping set times call!')
			return

		result = await self.multicall(
			('dedimania.SetChallengeTimes', self.session_id, {
				'UId': map.uid, 'Name': map.name, 'Environment': map.environment, 'Author': map.author_login,
				'NbCheckpoints': map.num_checkpoints, 'NbLaps': map.num_laps,
			}, game_mode, times, replays)
		)

		try:
			return bool(isinstance(result[0][0][0]['Records'], list))
		except Exception as e:
			pprint(result)
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

		self.new_index = None
		self.virtual_replay = None
		self.ghost_replay = ''
