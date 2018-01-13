"""
The MX Karma API client class.
"""
import logging
import aiohttp
import hashlib

from pyplanet import __version__ as version
from pyplanet.apps.contrib.mx.exceptions import MXInvalidResponse

logger = logging.getLogger(__name__)


class MXKarmaApi:
	def __init__(self, app):
		self.api_url = 'https://karma.mania-exchange.com/api2'
		self.app = app
		self.cookie_jar = aiohttp.CookieJar()
		self.session = None
		self.key = None
		self.activated = False

	async def create_session(self):
		if self.session is None:
			logger.debug('Creating session for MX Karma communication.')

			self.session = await aiohttp.ClientSession(
				cookie_jar=self.cookie_jar,
				headers={
					'User-Agent': 'PyPlanet/{}'.format(version),
					'X-ManiaPlanet-ServerLogin': self.app.app.instance.game.server_player_login
				}
			).__aenter__()

	async def close_session(self):
		if self.session and hasattr(self.session, '__aexit__'):
			logger.debug('Closing session for MX Karma communication.')

			await self.session.__aexit__()

	async def start_session(self):
		if self.session is None:
			await self.create_session()
		elif self.session is not None and self.key is None:
			logger.debug('Starting MX Karma session ...')

			url = '{url}/startSession?serverLogin={login}&applicationIdentifier={app}&testMode=true'.format(
				url=self.api_url, login=self.app.app.instance.game.server_player_login,
				app='PyPlanet {version}'.format(version=version)
			)

			response = await self.session.get(url)

			if response.status < 200 or response.status > 399:
				raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

			result = await response.json()
			self.key = result['data']['sessionKey']
			await self.activate_session(result['data']['sessionSeed'])

	async def activate_session(self, session_seed):
		api_key = await self.app.setting_mx_karma_key.get_value()
		hash = hashlib.sha512('{apikey}{seed}'.format(apikey=api_key, seed=session_seed).encode('utf-8')).hexdigest()

		url = '{url}/activateSession?sessionKey={key}&activationHash={hash}'.format(
			url=self.api_url, key=self.key, hash=hash
		)

		response = await self.session.get(url)

		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		result = await response.json()

		if result['success'] is False:
			self.activated = False
			logger.error('Error while getting information from ManiaExchange, error {code}: {message}'.format(
				code=result['data']['code'], message=result['data']['message']
			))
		else:
			self.activated = result['data']['activated']

			if self.activated:
				logger.info('Successfully started the MX Karma session.')
			else:
				logger.warning('Unable to start a MX Karma session.')

	async def get_map_rating(self, map, player_login = None):
		if not self.activated:
			return

		url = '{url}/getMapRating?sessionKey={key}'.format(
			url=self.api_url, key=self.key
		)

		votes_only = False
		logins = []
		if player_login is not None:
			votesonly = True
			logins = [player_login]
		else:
			logins = [login for login in self.app.app.instance.player_manager.online_logins]

		content = {
			'gamemode': await self.app.app.instance.mode_manager.get_current_script(),
			'titleid': self.app.app.instance.game.dedicated_title,
			'mapuid': map.uid,
			'getvotesonly': votes_only,
			'playerlogins': logins
		}

		response = await self.session.post(url, json=content)

		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		result = await response.json()

		if result['success'] is False:
			self.activated = False
			logger.error('Error while getting information from ManiaExchange, error {code}: {message}'.format(
				code=result['data']['code'], message=result['data']['message']
			))

			return None
		else:
			data = result['data']
			return data
