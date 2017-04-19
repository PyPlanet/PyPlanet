from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet.permissions import register_permissions


class ManiaplanetConfig(AppConfig):
	name = 'pyplanet.apps.core.maniaplanet'
	core = True

	async def on_init(self):
		# Register permissions.
		await register_permissions(self)

	async def on_start(self):
		# Register receivers context, only required if you use classmethods.
		#

		# Register commands.
		pass
