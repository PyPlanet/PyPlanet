
class _BaseUIManager:
	def __init__(self, instance):
		"""
		Initiate manager.
		
		:param instance: Instance of controller.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance
		self.manialinks = dict()

	async def send(self, manialink, logins=None, **kwargs):
		"""
		Send manialink to player(s).
		
		:param manialink: ManiaLink instance.
		:param logins: Logins to post to. None to globally send.
		:type manialink: pyplanet.core.ui.components.manialink._ManiaLink
		"""
		queries = list()
		for_logins = logins or (manialink.player_data.keys() if manialink.player_data else None)

		# Register to the manialink context.
		if manialink.id not in self.manialinks:
			self.manialinks[manialink.id] = manialink

		if not await manialink.is_global():
			for login in for_logins:
				if login not in manialink.player_data:
					continue

				if await manialink.get_template() and not manialink.body:
					body = await manialink.render(player_login=login)
				elif manialink.body:
					body = manialink.body
				else:
					raise Exception('Manialink has no body or template defined!')

				# Add manialink tag to body.
				body = '<manialink version="{}" id="{}">{}</manialink>'.format(manialink.version, manialink.id, body)

				# Prepare query
				queries.append(self.instance.gbx.prepare(
					'SendDisplayManialinkPageToLogin', login, body, manialink.timeout, manialink.hide_click
				))

		else:
			# Render/body
			if await manialink.get_template() and not manialink.body:
				body = await manialink.render()
			elif manialink.body:
				body = manialink.body
			else:
				raise Exception('Manialink has no body or template defined!')

			# Add manialink tag to body.
			body = '<manialink version="{}" id="{}">{}</manialink>'.format(manialink.version, manialink.id, body)

			if logins and len(logins) > 0:
				for login in logins:
					# Prepare query
					queries.append(self.instance.gbx.prepare(
						'SendDisplayManialinkPageToLogin', login, body, manialink.timeout, manialink.hide_click
					))
			else:
				# Prepare query
				queries.append(self.instance.gbx.prepare(
					'SendDisplayManialinkPage', body, manialink.timeout, manialink.hide_click
				))

		# Execute calls.
		await self.instance.gbx.multicall(*queries)

	async def hide(self, manialink, logins=None):
		"""
		Send manialink to player(s).
		
		:param manialink: ManiaLink instance.
		:param logins: Logins to post to. None to globally send.
		:type manialink: pyplanet.core.ui.components.manialink._ManiaLink
		"""
		body = '<manialink id="{}"></manialink>'.format(manialink.id)
		if logins and len(logins) > 0:
			await self.instance.gbx.execute('SendDisplayManialinkPageToLogin', ','.join(logins), body, 0, False)
		else:
			await self.instance.gbx.execute('SendDisplayManialinkPage', body, 0, False)

	async def destroy(self, manialink, logins=None):
		if manialink.id in self.manialinks:
			del self.manialinks[manialink.id]
		return await self.hide(manialink, logins)


class GlobalUIManager(_BaseUIManager):
	def __init__(self, instance):
		super().__init__(instance)
		self.app_managers = dict()

	def create_app_manager(self, app_config):
		"""
		Create app ui manager.
		
		:param app_config: App Config instance.
		:type app_config: pyplanet.apps.config.AppConfig
		:return: UI Manager
		:rtype: pyplanet.core.ui.AppUIManager
		"""
		if app_config.label not in self.app_managers:
			self.app_managers[app_config.label] = AppUIManager(self.instance, app_config)
		return self.app_managers[app_config.label]


class AppUIManager(_BaseUIManager):

	def __init__(self, instance, app):
		"""
		Initiate app ui manager.
		
		:param instance: Controller instance.
		:param app: App Config instance.
		:type instance: pyplanet.core.instance.Instance
		:type app: pyplanet.apps.config.AppConfig
		"""
		super().__init__(instance)
		self.app = app
