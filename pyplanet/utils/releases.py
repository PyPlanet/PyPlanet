import asyncio
import logging
import aiohttp

from . import semver


class _UpdateChecker:  # pragma: no cover

	def __init__(self):
		self.latest = None
		self.current = None
		self.instance = None

		self.url = 'https://api.github.com/repos/{}/tags'.format('PyPlanet/PyPlanet')

	async def init_checker(self, instance):
		"""
		Initiate checker.

		:param instance: Instance of controller.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance
		self.instance.signal_manager.listen('maniaplanet:player_connect', self.connect)

		asyncio.ensure_future(self.check(True))
		asyncio.ensure_future(self.loop())

	async def loop(self):
		while True:
			await asyncio.sleep(7200)  # 2 hours.
			try:
				await self.check()
			except:
				pass
		pass

	async def check(self, first_check=False):
		from pyplanet import __version__ as current_version

		logging.debug('Checking for new versions...')

		async with aiohttp.request('GET', self.url) as resp:
			self.latest = (await resp.json())[0]['name']
			self.current = current_version

			if first_check and self.update_available:
				logging.info('New version of PyPlanet available, consider updating: {}'.format(self.latest))
				await self.instance.chat(
					'\uf1e6 $FD4$oPy$369Planet$z$s$fff \uf0e7 new version available: v{}. Consider updating!'.format(self.latest)
				)

	@property
	def update_available(self):
		if self.latest is None or self.current is None:
			return False
		return semver.compare(self.latest, self.current) > 0

	async def connect(self, player, **kwargs):
		if player.level > 0 and self.update_available is not False:
			await self.instance.gbx.multicall(
				self.instance.chat(
					'\uf1e6 $FD4$oPy$369Planet$z$s$fff \uf0e7 new version available: v{}. Consider updating!'.format(self.latest),
					player
				),
				self.instance.chat(
					'$fffClick $l[http://pypla.net/intro/upgrading.html]here$l to open the upgrade instructions.',
					player
				)
			)

UpdateChecker = _UpdateChecker()
