import logging
import os

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.mx.api import MXApi
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
from pyplanet.apps.contrib.mx.view import MxSearchListView, MxPacksListView, MxStatusListView
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting
from collections import namedtuple

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
		await self.instance.permission_manager.register(
			'add_remote', 'Add map from remote source (such as MX)', app=self, min_level=2)
		await self.context.setting.register(
			self.setting_mx_key
		)

		await self.instance.command_manager.register(
			Command(command='info', namespace='mx', target=self.mx_info),
			# support backwards
			Command(command='mx', namespace='add', target=self.add_mx_map, perms='mx:add_remote', admin=True).add_param(
				'maps', nargs='*', type=str, required=True, help='MX ID(s) of maps to add.'),

			# new mx namespace
			Command(command='search', aliases=['list'], namespace='mx', target=self.search_mx_map, perms='mx:add_remote',
					admin=True),
			Command(command='add', namespace='mx', target=self.add_mx_map, perms='mx:add_remote', admin=True).add_param(
				'maps', nargs='*', type=str, required=True, help='MX ID(s) of maps to add.'),
			Command(command='status', namespace='mx', target=self.status_mx_maps, perms='mx:add_remote', admin=True),

			# new mxpack namespace
			Command(command='search', aliases=['list'], namespace='mxpack', target=self.search_mx_pack,
					perms='mx:add_remote', admin=True),
			Command(command='add', namespace='mxpack', target=self.add_mx_pack, perms='mx:add_remote', admin=True)
				.add_param('pack', nargs='*', type=str, required=True, help='MX ID(s) of mappacks to add.'),
		)

	async def mx_info(self, player, data, **kwargs):
		map_info = await self.api.map_info(self.instance.map_manager.current_map.uid)
		if len(map_info) != 1:
			message = '$f00Map could not be found on MX!'
			await self.instance.chat(message, player)
			return
		map_info = map_info[0][1]

		messages = [
			'$o$ff0Mania-Exchange info:$o Name: $fff{}$ff0, MX-username: $fff{}'.format(
				map_info['Name'], map_info['Username']
			)
		]
		if 'ReplayCount' in map_info:  # If TM with ReplayCount
			messages.append(
				'$ff0Number of replays: $fff{}$ff0, Number of awards: $fff{}$ff0, MX-ID: $l[{}]$fff{}$l $n(click to open MX)'.format(
					map_info['ReplayCount'], map_info['AwardCount'], 'https://{}.mania-exchange.com/s/tr/{}'.format(
						self.instance.game.game, map_info['TrackID']
					),
					map_info['TrackID']
				)
			)
		else:
			messages.append(
				'$ff0MX-ID: $l[{}]$fff{}$l (click to open MX)'.format(
					'https://{}.mania-exchange.com/s/tr/{}'.format(
						self.instance.game.game, map_info['MapID']
					),
					map_info['MapID']
				)
			)

		await self.instance.gbx.multicall(*[self.instance.chat(message, player) for message in messages])

	async def search_mx_pack(self, player, data, **kwargs):
		self.api.key = await self.setting_mx_key.get_value()
		window = MxPacksListView(self, player, self.api)
		await window.display()

	async def search_mx_map(self, player, data, **kwargs):
		self.api.key = await self.setting_mx_key.get_value()
		window = MxSearchListView(self, player, self.api)
		await window.display()

	async def status_mx_maps(self, player, data, **kwargs):
		self.api.key = await self.setting_mx_key.get_value()
		window = MxStatusListView(self, self.api)
		await window.display(player=player)

	async def add_mx_pack(self, player, data, **kwargs):
		try:
			pack_id = data.pack[0]
			token = data.pack[1] if len(data.pack) == 2 else ""
			ids = await self.api.get_pack_ids(pack_id, token)
			mx_ids = list()
			for obj in ids:
				mx_ids.append(str(obj[0]))

			mock = namedtuple("data", ["maps"])

			await self.instance.chat('$ff0MX: Installing mappack... This can take a while.', player)
			await self.add_mx_map(player, mock(maps=mx_ids))
			await self.instance.chat('$ff0MX: Done Installing mappack!', player)
		except MXMapNotFound:
			message = '$ff0Error: Can\'t add map pack from MX, due error.'
			await self.instance.chat(message, player)

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
			message = '$f00Error: Can\'t add map from MX. Map not found on ManiaExchange!'
			await self.instance.chat(message, player)
			return
		except MXInvalidResponse as e:
			message = '$f00Error: Got invalid response from ManiaExchange: {}'.format(str(e))
			await self.instance.chat(message, player.login)
			return

		try:
			if not await self.instance.storage.driver.exists(os.path.join('UserData', 'Maps', 'PyPlanet-MX')):
				await self.instance.storage.driver.mkdir(os.path.join('UserData', 'Maps', 'PyPlanet-MX'))
		except Exception as e:
			message = '$f00Error: Can\'t check or create folder: {}'.format(str(e))
			await self.instance.chat(message, player.login)
			return

		# Fetch setting if juke after adding is enabled.
		juke_after_adding = await self.instance.setting_manager.get_setting(
			'admin', 'juke_after_adding', prefetch_values=True)
		juke_maps = await juke_after_adding.get_value()
		if 'jukebox' not in self.instance.apps.apps:
			juke_maps = False
		juke_list = list()

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
					# Juke if setting has been provided.
					if juke_maps:
						juke_list.append(mx_info['MapUID'])

					message = '$ff0Admin $fff{}$z$s$ff0 has added{} the map $fff{}$z$s$ff0 by $fff{}$z$s$ff0 from MX..'.format(
						player.nickname, ' and juked' if juke_maps else '', mx_info['Name'], mx_info['Username']
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

		# Reindex and create maps in database.
		try:
			await self.instance.map_manager.update_list(full_update=True)
		except:
			pass

		# Jukebox all the maps requested, in order.
		if juke_maps and len(juke_list) > 0:
			# Fetch map objects.
			for juke_uid in juke_list:
				map_instance = await self.instance.map_manager.get_map(uid=juke_uid)
				if map_instance:
					self.instance.apps.apps['jukebox'].insert_map(player, map_instance)
