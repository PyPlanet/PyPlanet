import asyncio
import platform
import aiohttp

from json import dumps

from pyplanet import __version__ as version
from pyplanet.conf import settings


class _Analytics:
	URL = 'https://api.amplitude.com/httpapi'
	KEY = '4a33dd84e315e0b02066a7993043a6c7'

	def __init__(self):
		self.client = None
		self.instance = None

	async def execute(self, *event):
		if not settings.ANALYTICS or settings.DEBUG:
			return

		await self.client.post(self.URL, params=dict(api_key=self.KEY, event=dumps(event)))

	async def capture(
		self, event_name, event_properties=None
	):
		event_properties = event_properties or dict()
		user_properties = dict(
			path=self.instance.game.server_path,
			server_name=self.instance.game.server_name,
			language=self.instance.game.server_language,
			login=self.instance.game.server_player_login,
		)

		await self.execute(dict(
			user_id=self.instance.game.server_player_login,
			event_type=event_name, event_properties=event_properties, user_properties=user_properties,
			app_version=version, platform=platform.platform(), os_name=platform.system(), os_version=platform.version()
		))

	async def start(self, instance):
		"""
		Initiate the analytics.

		:param instance: Instance of controller.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance
		self.client = aiohttp.ClientSession()
		try:
			await self.capture('start_controller')
		except:
			pass

		# Start report loop
		asyncio.ensure_future(self.loop())

	async def loop(self):
		while True:
			await asyncio.sleep(60*5)
			try:
				await self.capture('online_ping', dict(
					total_players=self.instance.player_manager.count_all,
				))
			except:
				pass

Analytics = _Analytics()
