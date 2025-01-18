"""
The MX API client class.
"""
import asyncio
import logging
import aiohttp

from pyplanet import __version__ as pyplanet_version
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
from pyplanet.utils import times

logger = logging.getLogger(__name__)


class MXApi:
	def __init__(self, server_login=None):
		self.server_login = server_login
		self.cookie_jar = aiohttp.CookieJar()
		self.session = None
		self.site = None
		self.key = None
		self.map_info_page_size = 10
		self.difficulties = {
			0: 'Beginner',
			1: 'Intermediate',
			2: 'Advanced',
			3: 'Expert',
			4: 'Lunatic',
			5: 'Impossible'
		}
		self.environments = dict()

	def base_url(self, api=False):
		if self.site in ['tm', 'sm']:
			if api:
				return 'https://{site}.mania.exchange/api'.format(site=self.site)
			return 'https://{site}.mania.exchange'.format(site=self.site)
		elif self.site == 'tmnext':
			if api:
				return 'https://trackmania.exchange/api'
			return 'https://trackmania.exchange'

	async def create_session(self):
		self.session = await aiohttp.ClientSession(
			cookie_jar=self.cookie_jar,
			headers={
				'User-Agent': 'PyPlanet/{}'.format(pyplanet_version),
				'X-ManiaPlanet-ServerLogin': self.server_login
			}
		).__aenter__()

		if self.site == 'tmnext':
			self.environments = { 0: 'Custom', 1: 'Stadium'}
		elif self.site == 'sm':
			self.environments = {0: 'Custom', 1: 'Storm'}
		elif self.site == 'tm':
			self.environments = {
				0: 'Custom', 1: 'Canyon', 2: 'Stadium', 3: 'Valley', 4: 'Lagoon', 5: 'Desert',
				6: 'Snow', 7: 'Rally', 8: 'Coast', 9: 'Bay', 10: 'Island'
			}

	async def close_session(self):
		if self.session and hasattr(self.session, '__aexit__'):
			await self.session.__aexit__()

	async def mx_random(self, titlepack):
		url = '{}/maps?count=1&titlepack={}&random=1&fields=MapId'.format(
			self.base_url(api=True), titlepack,
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)

		if response.status == 404:
			raise MXMapNotFound('Got not found status from ManiaExchange: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		json = await response.json()
		if 'Results' in json and len(json['Results']) == 1:
			return str(json['Results'][0]['MapId'])

		return None

	async def search(self, titlepack, name=None, author=None, **kwargs):
		fields = [
			'MapId', 'MapUid', 'Name', 'GbxMapName', 'Uploader.Name',
			'Environment', 'AwardCount', 'Length', 'Difficulty', 'ServerSizeExceeded'
		]
		url = '{}/maps?count=100&titlepack={}{}{}&fields={}'.format(
			self.base_url(api=True), titlepack,
			'&name={}'.format(name) if name is not None and name != '' else '',
			'&author={}'.format(author) if author is not None and author != '' else '',
			'%2C'.join(fields)
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)

		if response.status == 404:
			raise MXMapNotFound('Got not found status from ManiaExchange: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		maps = list()
		json = await response.json()
		for info in json['Results']:
			info['Difficulty'] = self.difficulties[info['Difficulty']] if info['Difficulty'] in self.difficulties else 'Unknown'
			info['Environment'] = self.environments[info['Environment']] if info['Environment'] in self.environments else 'Unknown'
			info['Length'] = times.format_time(int(info['Length'])) if 'Length' in info else None
			maps.append(info)
		return maps

	async def search_pack(self, name, manager, **kwargs):
		fields = ['MappackId', 'Name', 'Owner.Name', 'MapCount', 'VideoUrl']
		url = '{}/mappacks?count=100{}{}&fields={}'.format(
			self.base_url(api=True),
			'&name={}'.format(name) if name is not None and name != '' else '',
			'&manager={}'.format(manager) if manager is not None and manager != '' else '',
			'%2C'.join(fields)
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)

		if response.status == 404:
			raise MXMapNotFound('Got not found status from ManiaExchange: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		maps = list()
		json = await response.json()
		if not 'Results' in json:
			return list()

		for info in json['Results']:
			maps.append(info)

		return maps

	async def map_info(self, *ids):
		if not len(ids):
			return list()
		if isinstance(ids, str) or isinstance(ids, int):
			# In case just one value is being passed, put it into an array.
			ids = [ids]

		# Split the map identifiers into groups, as the ManiaExchange API only accepts a limited amount of maps in one request.
		split_map_ids = [ids[i * self.map_info_page_size:(i + 1) * self.map_info_page_size] for i in range((len(ids) + self.map_info_page_size - 1) // self.map_info_page_size)]
		split_results = list()
		coros = list()
		for split_ids in split_map_ids:
			coros.append(self.map_info_page(split_ids))
		split_results = await asyncio.gather(*coros)

		# Join the multiple result lists back into one list.
		return [map for map_list in split_results for map in map_list]

	async def map_info_page(self, *ids):
		fields = ['MapId', 'MapUid', 'Name', 'Uploader.Name', 'UpdatedAt', 'ReplayCount', 'AwardCount', 'ServerSizeExceeded']
		mx_ids = ','.join([str(mx_id) for mx_id in ids[0] if str(mx_id).isnumeric()])
		uids = ','.join([uid for uid in ids[0] if not str(uid).isnumeric()])
		if len(mx_ids) > 0:
			mx_ids = '&id={}'.format(mx_ids)
		if len(uids) > 0:
			uids = '&uid={}'.format(uids)

		url = '{}/maps?count={}{}{}&fields={}'.format(
			self.base_url(api=True), self.map_info_page_size, mx_ids, uids, '%2C'.join(fields)
		)

		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)

		maps = list()
		json = await response.json()

		if response.status == 404 or 'Results' not in json or len(json['Results']) == 0:
			raise MXMapNotFound('Map has not been found!')
		if response.status == 302:
			raise MXInvalidResponse('Map author has declined info for the map. Status code: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		for info in json['Results']:
			maps.append((info['MapId'], info))
		return maps

	async def get_pack_ids(self, pack_id, token):
		url = '{}/maps?count=100&mappackid={}&fields=MapId'.format(
			self.base_url(api=True), pack_id
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)

		if response.status == 404:
			raise MXMapNotFound('Map pack not found!')
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		maps = list()
		json = await response.json()
		for info in json['Results']:
			maps.append((info['MapId'], info))

		return maps

	async def download(self, mx_id):
		url = '{}/mapgbx/{}'.format(
			self.base_url(api=True), mx_id
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)

		if response.status == 404:
			raise MXMapNotFound('Map has not been found!')
		if response.status == 302:
			raise MXInvalidResponse(
				'Map author has declined download of the map. Status code: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))
		return response
