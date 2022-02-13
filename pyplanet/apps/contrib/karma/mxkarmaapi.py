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
	"""
	MX Karma API Class will handle all the communication in async with the ManiaExchange Karma API.
	"""
	def __init__(self, app):
		self.api_url = 'https://karma.mania-exchange.com/api2'
		self.app = app
		self.cookie_jar = aiohttp.CookieJar()
		self.session = None
		self.key = None
		self.activated = False

	async def create_session(self):
		"""
		Create new async http session.
		"""
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
		"""
		Close the async http session
		"""
		if self.session and hasattr(self.session, '__aexit__'):
			logger.debug('Closing session for MX Karma communication.')

			await self.session.__aexit__(None, None, None)

	async def start_session(self):
		"""
		Create the MX Karma session by authenticating with the API. This method will make sure the server is ready
		to get and post karma entries to the API.
		"""
		if self.session is None:
			await self.create_session()
		elif self.session is not None and self.key is None:
			try:
				logger.debug('Starting MX Karma session ...')

				url = '{url}/startSession?serverLogin={login}&applicationIdentifier={app}&testMode=false'.format(
					url=self.api_url, login=self.app.app.instance.game.server_player_login,
					app='PyPlanet {version}'.format(version=version)
				)

				response = await self.session.get(url)

				if response.status < 200 or response.status > 399:
					raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

				result = await response.json()
				if result['success'] is False:
					logger.error('Error while starting ManiaExchange session, error {code}: {message}'.format(
						code=result['data']['code'], message=result['data']['message']
					))
				else:
					self.key = result['data']['sessionKey']
					await self.activate_session(result['data']['sessionSeed'])
			except (aiohttp.ClientConnectionError, aiohttp.ClientConnectorCertificateError):
				logger.warning('Unable to start a MX Karma session, server is unavailable.')
			except MXInvalidResponse:
				logger.warning('Unable to start a MX Karma session, invalid server response.')

	async def activate_session(self, session_seed):
		"""
		This method will activate the session based on the seed it created earlier.

		:param session_seed: Seed of the session created earlier.
		"""
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
		"""
		Get rating for the specific map instance.

		:param map: Map model instance.
		:param player_login: Player login, optional
		:return: Dictionary with data for the given map, received from the API.
		"""
		if not self.activated:
			return

		url = '{url}/getMapRating?sessionKey={key}'.format(
			url=self.api_url, key=self.key
		)

		logins = [vote.player.login for vote in self.app.app.current_votes]
		loop_logins = [logins[x:x+100] for x in range(0, len(logins), 100)]

		data = None

		for temp_logins in loop_logins:
			content = {
				'gamemode': await self.app.app.instance.mode_manager.get_current_full_script(),
				'titleid': self.app.app.instance.game.dedicated_title,
				'mapuid': map.uid,
				'getvotesonly': False,
				'playerlogins': temp_logins
			}

			response = await self.session.post(url, json=content)

			if response.status < 200 or response.status > 399:
				raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

			result = await response.json()

			if result['success'] is False:
				logger.error('Error while getting information from ManiaExchange, error {code}: {message}'.format(
					code=result['data']['code'], message=result['data']['message']
				))

				return None
			else:
				if data is None:
					data = result['data']
				else:
					data['votes'] += result['data']['votes']

		if data and 'votes' in data:
			logger.debug('Amount of MX Karma votes retrieved for this map: {}'.format(len(data['votes'])))

		return data

	async def save_votes(self, map, is_import=False, map_length=0, votes=None):
		"""
		Save votes to the MX Karma API.

		:param map: Map instance
		:param is_import: State if the votes are imported from local karma.
		:param map_length: Map length.
		:param votes: Votes payload.
		:return: Status or updated value.
		"""
		if not self.activated:
			return

		if votes is None:
			return

		url = '{url}/saveVotes?sessionKey={key}'.format(
			url=self.api_url, key=self.key
		)

		content = {
			'gamemode': await self.app.app.instance.mode_manager.get_current_full_script(),
			'titleid': self.app.app.instance.game.dedicated_title,
			'mapuid': map.uid,
			'mapname': map.name,
			'mapauthor': map.author_login,
			'isimport': is_import,
			'maptime': map_length,
			'votes': votes
		}

		response = await self.session.post(url, json=content)

		if response.status < 200 or response.status > 399:
			raise MXInvalidResponse('Got invalid response status from ManiaExchange: {}'.format(response.status))

		result = await response.json()

		if result['success'] is False:
			logger.error('Error while saving information to ManiaExchange, error {code}: {message}'.format(
				code=result['data']['code'], message=result['data']['message']
			))
			return False
		else:
			if votes is not None:
				logger.debug('Amount of MX Karma votes saved for this map: {}'.format(len(votes)))
			return result['data']['updated']
