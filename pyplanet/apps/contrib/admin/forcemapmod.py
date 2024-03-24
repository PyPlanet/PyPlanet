import logging

from pyplanet.contrib.setting import Setting

logger = logging.getLogger(__name__)


class ForceMapMod:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance
		self.force_mod_urls = Setting(
			'force_mod_urls', 'ForceMod - forces a map texture modification', Setting.CAT_FEATURES, type=list,
			description='Format for each line is:\nEnvironmentName|https://your.url.here/texturemod.zip',
			default=[],
			change_target=self.on_modchange
		)
		self.force_mod_override = Setting(
			'force_mod_override', 'ForceMod - override map texture mods', Setting.CAT_FEATURES, type=bool,
			description='When true, the maps with existing mod will be overridden by this setting.',
			default=False,
			change_target=self.on_modchange
		)

	async def on_start(self):
		await self.app.context.setting.register(self.force_mod_urls)
		await self.app.context.setting.register(self.force_mod_override)

		await self.update_mod()

	async def on_modchange(self, *args, **kwargs):
		await self.update_mod()

	async def update_mod(self):
		mods = await self.force_mod_urls.get_value(True)
		override = await self.force_mod_override.get_value(True)

		if not len(mods):
			await self.instance.gbx.execute('SetForcedMods', False, list())
			return

		force = []
		for mod in mods:
			value = mod.split('|')
			if len(value) == 2:
				force.append({'Env': value[0], 'Url': value[1]})
			else:
				logger.warning('Some force-mods are not in the correct format: Env|Url, skipping! Change in //settings')
		try:
			await self.instance.gbx.execute('SetForcedMods', override, force)
			logger.debug('Forcing map mods is now set!')
		except Exception as err:
			logger.error('Setting Map Force Mods failed from the MP-server: ' + str(err))
