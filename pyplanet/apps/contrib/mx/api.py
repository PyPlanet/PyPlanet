"""
The MX API client class.
"""
import logging

import aiohttp

from pyplanet import __version__ as pyplanet_version
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse

logger = logging.getLogger(__name__)


class MXApi:
	def __init__(self, server_login=None):
		self.server_login = server_login
		self.cookie_jar = aiohttp.CookieJar()
		self.session = None
		self.site = None
		self.key = None
		self.map_info_page_size = 50

	async def create_session(self):
		self.session = await aiohttp.ClientSession(
			cookie_jar=self.cookie_jar,
			headers={
				'User-Agent': 'PyPlanet/{}'.format(pyplanet_version),
				'X-ManiaPlanet-ServerLogin': self.server_login
			}
		).__aenter__()

	async def close_session(self):
		if self.session and hasattr(self.session, '__aexit__'):
			await self.session.__aexit__()

	async def search(self, options, **kwargs):
		if options is None:
			options = {
				"api": "on",
				"mode": 0,
				"style": 0,
				"order": -1,
				"length": -1,
				"page": 0,
				"gv": 1,
				"limit": 150
			}

		if self.key:
			options['key'] = self.key

		url = 'https://{site}.mania-exchange.com/tracksearch2/search'.format(
			site=self.site
		)
		response = await self.session.get(url, params=options)

		if response.status == 404:
			raise MXMapNotFound('Got not found status from ManiaExchange: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		maps = list()
		json = await response.json()
		for info in json['results']:
			# Parse some differences between the api game endpoints.
			mx_id = info['TrackID'] if 'TrackID' in info else info['MapID']
			info['MapID'] = mx_id
			info['MapUID'] = info['TrackUID'] if 'TrackUID' in info else info['MapUID']
			maps.append(info)
		return maps

	async def search_pack(self, options, **kwargs):
		if options is None:
			options = dict()

		if self.key:
			options['key'] = self.key

		options['api'] = 'on'

		url = 'https://{site}.mania-exchange.com/mappacksearch/search'.format(
			site=self.site
		)
		response = await self.session.get(url, params=options)

		if response.status == 404:
			raise MXMapNotFound('Got not found status from ManiaExchange: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		maps = list()
		json = await response.json()
		if not 'results' in json:
			return list()

		for info in json['results']:
			# Parse some differences between the api game endpoints.
			maps.append(info)

		return maps

	async def map_info(self, *ids):
		if isinstance(ids[0], str) or isinstance(ids[0], int):
			# In case just one value is being passed, put it into an array.
			ids = [ids]

		# Split the map identifiers into groups, as the ManiaExchange API only accepts a limited amount of maps in one request.
		map_ids = ids[0]
		split_map_ids = [map_ids[i * self.map_info_page_size:(i + 1) * self.map_info_page_size] for i in range((len(map_ids) + self.map_info_page_size - 1) // self.map_info_page_size)]
		split_results = []
		for split_ids in split_map_ids:
			split_results.append(await self.map_info_page(split_ids))

		# Join the multiple result lists back into one list.
		return [map for map_list in split_results for map in map_list]

	async def map_info_page(self, *ids):
		url = 'https://api.mania-exchange.com/{site}/maps/{ids}'.format(
			site=self.site,
			ids=','.join(str(id) for id in ids[0])
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)
		if response.status == 404:
			raise MXMapNotFound('Map has not been found!')
		if response.status == 302:
			raise MXInvalidResponse('Map author has declined info for the map. Status code: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))
		maps = list()
		for info in await response.json():
			# Parse some differences between the api game endpoints.
			mx_id = info['TrackID'] if 'TrackID' in info else info['MapID']
			info['MapID'] = mx_id
			info['MapUID'] = info['TrackUID'] if 'TrackUID' in info else info['MapUID']
			maps.append((mx_id, info))
		return maps

	async def pack_info(self, id, token):
		url = 'https://{site}.mania-exchange.com/api/mappack/get_info/{id}?token={token}'.format(
			site=self.site,
			id=id,
			token=token
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)
		if response.status == 404:
			raise MXMapNotFound('Map has not been found!')
		if response.status == 302:
			raise MXInvalidResponse('Map author has declined info for the map. Status code: {}'.format(response.status))
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		return response.json()

	async def get_pack_ids(self, pack_id, token):
		url = 'https://{site}.mania-exchange.com/api/mappack/get_tracks/{id}?token={token}'.format(
			site=self.site,
			id=pack_id,
			token=token
		)
		params = {'key': self.key} if self.key else {}
		response = await self.session.get(url, params=params)
		if response.status == 404:
			raise MXMapNotFound('Map pack not found!')
		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))
		maps = list()
		if response.content_length > 0:
			for info in await response.json():
				# Parse some differences between the api game endpoints.
				mx_id = info['TrackID']
				maps.append((mx_id, info))

			return maps
		else:
			raise MXMapNotFound("Mx returned with empty response.")

	async def download(self, mx_id):
		url = 'https://{site}.mania-exchange.com/tracks/download/{id}'.format(
			site=self.site,
			id=mx_id,
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
