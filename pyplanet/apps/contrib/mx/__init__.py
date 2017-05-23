import logging
import os

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.mx.api import MXApi
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting

logger = logging.getLogger(__name__)


class MX(AppConfig):  # pragma: no cover
	name = 'pyplanet.apps.contrib.mx'
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.api = MXApi()

		self.setting_mx_key = Setting(
			'mx_key', 'ManiaExchange Key', Setting.CAT_KEYS, type=str, default=None,
			description='Is only required when you want to download from a private group/section!'
		)

	async def on_init(self):
		# Set server login in the API.
		self.api.server_login = self.instance.game.server_player_login
		# Set the default site in.
		self.api.site = self.instance.game.game

		await self.api.create_session()

	async def on_start(self):
		await self.instance.permission_manager.register('add_remote', 'Add map from remote source (such as MX)', app=self, min_level=2)
		await self.context.setting.register(
			self.setting_mx_key
		)
		await self.instance.command_manager.register(
			Command(command='mx', namespace='add', target=self.add_mx_map, perms='mx:add_remote', admin=True)
				.add_param('maps', nargs='*', type=str, required=True, help='MX ID(s) of maps to add.'),
				)

	async def add_mx_map(self, player, data, **kwargs):
		# Make sure we update the key in the api.
		self.api.key = await self.setting_mx_key.get_value()

		# Prepare and fetch information about the maps from MX.
		mx_ids = data.maps

		try:
			infos = await self.api.map_info(*mx_ids)
			if len(infos) == 0:
				raise MXMapNotFound()
		except MXMapNotFound:
			message = '$ff0Error: Can\'t add map from MX. Map not found on ManiaExchange!'
			await self.instance.chat(message, player)
			return
		except MXInvalidResponse as e:
			message = '$ff0Error: Got invalid response from ManiaExchange: {}'.format(str(e))
			await self.instance.chat(message, player.login)
			return

		try:
			if not await self.instance.storage.driver.exists(os.path.join('UserData', 'Maps', 'PyPlanet-MX')):
				await self.instance.storage.driver.mkdir(os.path.join('UserData', 'Maps', 'PyPlanet-MX'))
		except Exception as e:
			message = '$ff0Error: Can\'t check or create folder: {}'.format(str(e))
			await self.instance.chat(message, player.login)
			return

		for mx_id, mx_info in infos:
			if 'Name' not in mx_info:
				continue

			try:
				# Test if map isn't yet in our current map list.
				if self.instance.map_manager.playlist_has_map(mx_info['MapUID']):
					raise Exception('Map already in playlist! Update? remove it first!')

				# Download file + save
				resp = await self.api.download(mx_id)
				map_filename = os.path.join('PyPlanet-MX', '{}-{}.Map.Gbx'.format(
					self.instance.game.game.upper(), mx_id
				))
				async with self.instance.storage.open_map(map_filename, 'wb+') as map_file:
					await map_file.write(await resp.read())
					await map_file.close()

				# Insert map to server.
				result = await self.instance.map_manager.add_map(map_filename, save_matchsettings=False)

				if result:
					message = '$ff0Admin $fff{}$z$s$ff0 has added the map $fff{}$z$s$ff0 by $fff{}$z$s$ff0 from MX..'.format(
						player.nickname, mx_info['Name'], mx_info['Username']
					)
					await self.instance.chat(message)
				else:
					raise Exception('Unknown error while adding the map!')
			except Exception as e:
				logger.warning('Error when player {} was adding map from mx: {}'.format(player.login, str(e)))
				message = '$ff0Error: Can\'t add map {}, Error: {}'.format(mx_info['Name'], str(e))
				await self.instance.chat(message, player.login)

		# Save match settings after inserting maps.
		try:
			await self.instance.map_manager.save_matchsettings()
		except:
			pass
