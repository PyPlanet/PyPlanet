import logging
import os

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.apps.contrib.mx.api import MXApi
from pyplanet.apps.contrib.mx.exceptions import MXMapNotFound, MXInvalidResponse
from pyplanet.apps.contrib.mx.view import MxSearchListView, MxPacksListView, MxStatusListView, MxAwardWidget
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting
from collections import namedtuple

from pyplanet.utils import gbxparser

logger = logging.getLogger(__name__)


class MX(AppConfig):  # pragma: no cover
	name = 'pyplanet.apps.contrib.mx'
	game_dependencies = ['trackmania', 'trackmania_next', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.api = MXApi()

		self.namespace = 'mx'
		self.site_name = 'ManiaExchange'
		self.site_short_name = 'MX'
		self.award_widget = None

		self.setting_mx_key = Setting(
			'mx_key', 'ManiaExchange/TrackmaniaExchange Key', Setting.CAT_KEYS, type=str, default=None,
			description='Is only required when you want to download from a private group/section!'
		)
		self.setting_display_award_widget = Setting(
			'display_award_widget', 'Display the award widget on podium', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether to display the widget linking to the MX award page on podium.', default=True
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
			self.setting_mx_key, self.setting_display_award_widget
		)

		self.award_widget = MxAwardWidget(self)

		if self.instance.game.game == 'tmnext':
			self.namespace = 'tmx'
			self.site_name = 'TrackmaniaExchange'
			self.site_short_name = 'TMX'

		await self.instance.command_manager.register(
			Command(command='info', namespace=self.namespace, target=self.mx_info,
					description='Display ManiaExchange/TrackmaniaExchange information for current map.'),
			# support backwards
			Command(command='mx', namespace='add', target=self.add_mx_map, perms='mx:add_remote', admin=True,
					description='Add map from ManiaExchange to the maplist.').add_param(
				'maps', nargs='*', type=str, required=True, help='MX ID(s) of maps to add.'),
			# new mx command random (Adding) Random Maps from MX
			Command(command='random', namespace=self.namespace, target=self.random_mx_map, perms='mx:add_remote',
					admin=True, description='Get Random Maps on ManiaExchange/TrackmaniaExchange.'),
			# new mx namespace
			Command(command='search', aliases=['list'], namespace=self.namespace, target=self.search_mx_map, perms='mx:add_remote',
					admin=True, description='Search for maps on ManiaExchange/TrackmaniaExchange.'),
			Command(command='add', namespace=self.namespace, target=self.add_mx_map, perms='mx:add_remote', admin=True,
					description='Add map from ManiaExchange/TrackmaniaExchange to the maplist.').add_param(
				'maps', nargs='*', type=str, required=True, help='MX/TMX ID(s) of maps to add.'),
			Command(command='status', namespace=self.namespace, target=self.status_mx_maps, perms='mx:add_remote', admin=True,
					description='View the map statuses compared to ManiaExchange/TrackmaniaExchange.'),

			# new mxpack namespace
			Command(command='search', aliases=['list'], namespace='{}pack'.format(self.namespace), target=self.search_mx_pack,
					perms='mx:add_remote', admin=True, description='Search for mappacks on ManiaExchange/TrackmaniaExchange.'),
			Command(command='add', namespace='{}pack'.format(self.namespace), target=self.add_mx_pack, perms='mx:add_remote',
					admin=True, description='Add mappack from ManiaExchange/TrackmaniaExchange to the maplist.')
				.add_param('pack', nargs='*', type=str, required=True, help='MX/TMX ID(s) of mappacks to add.'),
		)

		# Register callbacks.
		# Use podium end for regular map changes, the map start is required in case the map get restarted during the podium.
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.context.signals.listen(mp_signals.flow.podium_end, self.podium_end)
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)

	async def podium_start(self, **kwargs):
		if await self.setting_display_award_widget.get_value() is True:
			mx_info = await self.api.map_info(self.instance.map_manager.current_map.uid)
			if mx_info and len(mx_info) >= 1:
				self.award_widget.mx_id = mx_info[0][0]

				# Only display the award widget to the playing players.
				play_logins = [p.login for p in self.instance.player_manager.online if not p.flow.is_spectator]
				await self.award_widget.display(player_logins=play_logins)

	async def podium_end(self, **kwargs):
		await self.award_widget.hide()

	async def map_start(self, map, restarted, **kwargs):
		await self.award_widget.hide()

	async def random_mx_map(self, player, data, **kwargs):
		map_random_id = await self.api.mx_random()
		await self.instance.command_manager.execute(
			player,
			'//{} add maps'.format(self.namespace),
			str(map_random_id)
		)

	async def mx_info(self, player, data, **kwargs):
		try:
			map_info = await self.api.map_info(self.instance.map_manager.current_map.uid)
		except Exception as e:
			map_info = list()
			logger.error('Could not retrieve map info from MX/TM API: {}'.format(str(e)))
		if len(map_info) != 1:
			message = '$f00Map could not be found on MX!'
			await self.instance.chat(message, player)
			return
		map_info = map_info[0][1]

		messages = [
			'$o$ff0{site_name} info:$o Name: $fff{map_name}$ff0, {site_code}-username: $fff{map_username}'.format(
				site_name=self.site_name,
				site_code=self.site_short_name,
				map_name=map_info['Name'],
				map_username=map_info['Username'],
			)
		]
		if 'ReplayCount' in map_info:  # If TM with ReplayCount
			messages.append(
				'$ff0Number of replays: $fff{num_replays}$ff0, Number of awards: $fff{num_awards}$ff0, {site_code}-ID: $l[{link}]$fff{id}$l $n(click to open {site_code})'.format(
					num_replays=map_info['ReplayCount'],
					num_awards=map_info['AwardCount'],
					site_code=self.site_short_name,
					link='{}/s/tr/{}'.format(self.api.base_url(), map_info['TrackID']),
					id=map_info['TrackID'],
				)
			)
		else:
			messages.append(
				'$ff0{site_code}-ID: $l[{link}]$fff{id}$l (click to open {site_code})'.format(
					site_code=self.site_short_name,
					link='{}/s/tr/{}'.format(self.api.base_url(), map_info['MapID']),
					id=map_info['MapID']
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
		await self.instance.chat('$ff0{site_code}: Please wait, checking for updated maps... This can take a while.'.format(
			site_code=self.site_short_name
		), player)
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

			await self.instance.chat('$ff0{}: Installing mappack... This can take a while.'.format(self.site_short_name), player)
			await self.add_mx_map(player, mock(maps=mx_ids))
			await self.instance.chat('$ff0{}: Done Installing mappack!'.format(self.site_short_name), player)
		except MXMapNotFound:
			message = '$ff0Error: Can\'t add map pack from {}, due error.'.format(self.site_short_name)
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
			message = '$f00Error: Can\'t add map from {}. Map not found on {}!'.format(self.site_short_name, self.site_name)
			await self.instance.chat(message, player)
			return
		except MXInvalidResponse as e:
			message = '$f00Error: Got invalid response from {}: {}'.format(self.site_name, str(e))
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
		added_map_uids = list()

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
					added_map_uids.append(mx_info['MapUID'])

					message = '$ff0Admin $fff{}$z$s$ff0 has added{} the map $fff{}$z$s$ff0 by $fff{}$z$s$ff0 from {}..'.format(
						player.nickname, ' and juked' if juke_maps else '', mx_info['Name'], mx_info['Username'], self.site_short_name
					)
					await self.instance.chat(message)
				else:
					raise Exception('Unknown error while adding the map!')
			except Exception as e:
				logger.warning('Error when player {} was adding map from {}: {}'.format(player.login, self.site_short_name, str(e)))
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
		if juke_maps and len(added_map_uids) > 0:
			# Fetch map objects.
			for juke_uid in added_map_uids:
				map_instance = await self.instance.map_manager.get_map(uid=juke_uid)
				if map_instance:
					self.instance.apps.apps['jukebox'].insert_map(player, map_instance)

		return [await self.instance.map_manager.get_map(uid=added_uid) for added_uid in added_map_uids]
