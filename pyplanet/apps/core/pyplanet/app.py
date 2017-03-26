from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.pyplanet.permissions import register_permissions


class PyPlanetConfig(AppConfig):
	name = 'pyplanet.apps.core.pyplanet'
	core = True

	async def on_init(self):
		# Register permissions.
		await register_permissions(self)
