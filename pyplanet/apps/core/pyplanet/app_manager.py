"""
App manager component.
"""
import asyncio
import json
import logging

import aiohttp

from datetime import datetime, timedelta
from pyplanet.conf import settings
from pyplanet.utils import semver
from pyplanet.utils.pip import Pip
from pyplanet import __version__ as pyplanet_version

logger = logging.getLogger(__name__)


class AppManagerComponent:
	def __init__(self, app):
		"""
		App manager component

		:param app: App config instance
		:type app: pyplanet.apps.core.pyplanet.app.PyPlanetConfig
		"""
		self.app = app
		self.pip = Pip()
		self.index_file = "https://raw.githubusercontent.com/TheMaximum/PyPlanet-index/main/index.json"
		self.pypi_file = "https://pypi.org/pypi/{}/json"
		self.last_retrieval = None
		self.session = None
		self.apps = []

	async def on_init(self):
		self.session = await aiohttp.ClientSession(headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}).__aenter__()
		await self.load_packages()

		logger.info("Third-party apps available: {} (installed: {})".format(len(self.apps), len([a for a in self.apps if a['configured']])))
		logger.debug("Available apps: {}".format(", ".join(["{} ({})".format(a['package'], a['latest_version']) for a in self.apps])))
		logger.debug("Installed apps: {}".format(", ".join(["{} ({})".format(a['package'], a['installed_version']) for a in self.apps if a['configured']])))
		if any([a for a in self.apps if a['outdated']]):
			logger.warning("Outdated apps: {}".format(", ".join(["{} ({} -> {})".format(a['package'], a['installed_version'], a['latest_version']) for a in self.apps if a['outdated']])))
		logger.debug(self.apps)

	async def on_start(self):
		pass

	async def load_packages(self):
		"""
		Loads the installed packages from pip and the available app packages from the online index.
		Will filter the installed packages based on the app packages, to determine which packages to display.
		"""
		if self.last_retrieval is not None and (self.last_retrieval + timedelta(minutes=15)) > datetime.now():
			# Only allow refresh of the packages list every 15 minutes.
			logger.debug("Last package retrieval occured at {}, using cached date (min. 15 minutes)".format(self.last_retrieval))
			return

		installed_packages = self.pip.list()
		response = await self.session.get(self.index_file)
		response_content = await response.text()
		available_packages = json.loads(response_content)

		installed_packages = {ip['name']: ip['version'] for ip in installed_packages}
		self.apps = [dict(package=a['package'], description=None, app=a['app'],
			installed_version=installed_packages[a['package']] if a['package'] in installed_packages else None,
			latest_version=None, outdated=False,
		    configured=a['app'] in settings.APPS[self.app.instance.process_name]) for a in available_packages]

		coros = list()
		for app in self.apps:
			coros.append(self.get_pypi_info(app))
		await asyncio.gather(*coros)

		self.last_retrieval = datetime.now()

	async def get_pypi_info(self, app):
		package_response = await self.session.get(self.pypi_file.format(app['package']))
		package_info = await package_response.json()
		if 'info' not in package_info:
			return

		app['latest_version'] = package_info['info']['version']
		if app['installed_version'] is not None:
			app['outdated'] = semver.compare(app['latest_version'], app['installed_version']) > 0
		if 'summary' in package_info['info']:
			app['description'] = package_info['info']['summary']
