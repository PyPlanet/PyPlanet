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

	async def map_info(self, *ids):
		url = 'https://api.mania-exchange.com/{site}/maps/{ids}'.format(
			site=self.site,
			ids=','.join(ids)
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
