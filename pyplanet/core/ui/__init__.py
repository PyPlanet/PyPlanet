import asyncio
import logging

from xmlrpc.client import Fault

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.ui.ui_properties import UIProperties
from pyplanet.utils.log import handle_exception

logger = logging.getLogger(__name__)


class _BaseUIManager:
	def __init__(self, instance):
		"""
		Initiate manager.

		:param instance: Instance of controller.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance
		self.manialinks = dict()
		self.send_queue = list()

	async def on_start(self):
		asyncio.ensure_future(self.send_loop())

	async def send_loop(self):
		while True:
			await asyncio.sleep(0.25)
			if len(self.send_queue) == 0:
				continue

			# Copy send queue and clear the global one
			queue = self.send_queue.copy()
			self.send_queue.clear()

			# Process and push out the queue.
			try:
				await self.instance.gbx.multicall(*queue)
			except Fault as e:
				if 'Login unknown' in str(e):
					return
				logger.exception(e)
				handle_exception(exception=e, module_name=__name__, func_name='send_loop')
			except Exception as e:
				logger.exception(e)
				handle_exception(exception=e, module_name=__name__, func_name='send_loop')

	async def send(self, manialink, players=None, **kwargs):
		"""
		Send manialink to player(s).

		:param manialink: ManiaLink instance.
		:param players: Player instances or logins to post to. None to globally send.
		:type manialink: pyplanet.core.ui.components.manialink._ManiaLink
		"""
		queries = list()
		if isinstance(players, list):
			for_logins = [p.login if isinstance(p, Player) else p for p in players]
		elif manialink.player_data:
			for_logins = list(manialink.player_data.keys())
		else:
			for_logins = list()

		# Register to the manialink context.
		if manialink.id not in self.manialinks:
			self.manialinks[manialink.id] = manialink

		is_global = await manialink.is_global()
		if not is_global:
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
				queries.append(self.instance.gbx(
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

			# Add normal queries.
			if for_logins and len(for_logins) > 0:
				for login in for_logins:
					# Prepare query
					queries.append(self.instance.gbx(
						'SendDisplayManialinkPageToLogin', login, body, manialink.timeout, manialink.hide_click
					))
			else:
				# Prepare query
				queries.append(self.instance.gbx(
					'SendDisplayManialinkPage', body, manialink.timeout, manialink.hide_click
				))

		# Hide ALT menus (shootmania).
		if self.instance.game.game == 'sm' and manialink.disable_alt_menu:
			if is_global:
				queries.extend([
					self.instance.gbx('Maniaplanet.UI.SetAltScoresTableVisibility', player.login, 'false', encode_json=False, response_id=False)
					for player in self.instance.player_manager.online
				])
			else:
				queries.extend([
					self.instance.gbx('Maniaplanet.UI.SetAltScoresTableVisibility', login, 'false', encode_json=False, response_id=False)
					for login in for_logins
				])

		# It the manialink wants rate limitting with the relaxed updating feature (mostly used for widgets), add to send queue
		if getattr(manialink, 'relaxed_updating', False):
			self.send_queue.extend(queries)
			return

		# Execute calls, ignore login unknown (player just left).
		try:
			await self.instance.gbx.multicall(*queries)
		except Fault as e:
			if 'Login unknown' in str(e):
				return
			raise

	async def hide(self, manialink, logins=None):
		"""
		Send manialink to player(s).

		:param manialink: ManiaLink instance.
		:param logins: Logins to post to. None to globally send.
		:type manialink: pyplanet.core.ui.components.manialink._ManiaLink
		"""
		body = '<manialink id="{}"></manialink>'.format(manialink.id)
		queries = list()
		if logins and len(logins) > 0:
			queries.append(
				self.instance.gbx('SendDisplayManialinkPageToLogin', ','.join(logins), body, 0, False)
			)

			# Show alt menu again.
			if self.instance.game.game == 'sm' and manialink.disable_alt_menu:
				queries.extend([
					self.instance.gbx('Maniaplanet.UI.SetAltScoresTableVisibility', login, 'true', encode_json=False, response_id=False)
					for login in logins
				])
		else:
			queries.append(self.instance.gbx('SendDisplayManialinkPage', body, 0, False))
			if self.instance.game.game == 'sm' and manialink.disable_alt_menu:
				queries.extend([
					self.instance.gbx('Maniaplanet.UI.SetAltScoresTableVisibility', player.login, 'true', encode_json=False, response_id=False)
					for player in self.instance.player_manager.online
				])

		# It the manialink wants rate limitting with the relaxed updating feature (mostly used for widgets), add to send queue
		if getattr(manialink, 'relaxed_updating', False):
			self.send_queue.extend(queries)
			return

		# Execute queries.
		await self.instance.gbx.multicall(*queries)

	async def destroy(self, manialink, logins=None):
		if manialink.id in self.manialinks:
			del self.manialinks[manialink.id]
		return await self.hide(manialink, logins)


class GlobalUIManager(_BaseUIManager):
	def __init__(self, instance):
		super().__init__(instance)
		self.app_managers = dict()
		self.properties = UIProperties(self.instance)

	async def on_start(self):
		await super().on_start()
		await self.properties.on_start()

		# Start app ui managers.
		await asyncio.gather(*[
			m.on_start() for m in self.app_managers.values()
		])

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
