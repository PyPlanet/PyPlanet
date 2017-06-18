import asyncio
import logging
import uuid

from requests.exceptions import ConnectionError as RequestsConnectionError

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.dedimania.api import DedimaniaAPI, DedimaniaRecord
from pyplanet.apps.contrib.dedimania.exceptions import DedimaniaException, DedimaniaTransportException, \
	DedimaniaNotSupportedException, DedimaniaFault, DedimaniaInvalidCredentials
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting
from pyplanet.utils import times
from pyplanet.utils.log import handle_exception

from .views import DedimaniaRecordsWidget, DedimaniaRecordsListView

logger = logging.getLogger(__name__)


class Dedimania(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.widget = None
		self.api = None

		self.lock = asyncio.Lock()
		self.current_records = []
		self.current_script = None
		self.player_info = dict()

		self.v_replay = None
		self.v_replay_checks = None
		self.ghost_replay = None

		self.server_max_rank = None
		self.map_status = None
		self.map_uid = None
		self.ready = False

		self.setting_server_login = Setting(
			'server_login', 'Dedimania Server Login', Setting.CAT_KEYS, type=str,
			description='Only fill in when you want to override the auto-detected server login!',
			default=None, change_target=self.reload_settings
		)
		self.setting_dedimania_code = Setting(
			'dedimania_code', 'Dedimania Server Code', Setting.CAT_KEYS, type=str,
			description='The secret dedimania code. Get one at $lhttp://dedimania.net/tm2stats/?do=register',
			default=None, change_target=self.reload_settings
		)

		self.setting_chat_announce = Setting(
			'chat_announce', 'Minimum index for chat announce', Setting.CAT_BEHAVIOUR, type=int,
			description='Minimum record index needed for public new record/recordchange announcement (0 for disable).',
			default=50
		)
		self.setting_sent_announce = Setting(
			'sent_announce', 'Announce sending times to dedimania', Setting.CAT_BEHAVIOUR, type=bool,
			description='Enable the announce of successfully sent records to dedimania message.',
			default=False
		)

		self.login = self.code = self.server_version = self.pack_mask = None

	def is_mode_supported(self, mode):
		mode = mode.lower()
		return mode.startswith('timeattack') or mode.startswith('rounds') or mode.startswith('team') or \
			   mode.startswith('laps') or mode.startswith('cup')

	async def on_start(self):
		# Init settings.
		await self.context.setting.register(
			self.setting_server_login, self.setting_dedimania_code, self.setting_chat_announce, self.setting_sent_announce,
		)

		# Load settings + initiate api.
		await self.reload_settings()

		# Register signals
		self.instance.signal_manager.listen(mp_signals.map.map_begin, self.map_begin)
		self.instance.signal_manager.listen(mp_signals.map.map_start, self.map_start)
		self.instance.signal_manager.listen(mp_signals.map.map_end, self.map_end)

		# TODO Activate after server bug has fixed!
		# self.instance.signal_manager.listen(mp_signals.flow.podium_start, self.podium_start)

		self.instance.signal_manager.listen(tm_signals.finish, self.player_finish)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)
		self.instance.signal_manager.listen(mp_signals.player.player_disconnect, self.player_disconnect)

		# Change round results widget location.

		# Load initial data.
		self.widget = DedimaniaRecordsWidget(self)

	async def reload_settings(self, *args, **kwargs):
		# Check setting + return errors if not correct!
		self.login = await self.setting_server_login.get_value(refresh=True) or self.instance.game.server_player_login
		self.code = await self.setting_dedimania_code.get_value(refresh=True)
		if not self.code:
			message = '$0b3Error: No dedimania code was provided, please edit the settings (//settings).'
			logger.error('Dedimania Code not configured! Please configure with //settings!')
			await self.instance.chat(message)
			return

		# Save current script name
		self.current_script = await self.instance.mode_manager.get_current_script()

		# Init API (execute this in a non waiting future).
		self.api = DedimaniaAPI(
			self.instance,
			self.login, self.code, self.instance.game.server_path, self.instance.map_manager.current_map.environment,
			self.instance.game.dedicated_version, self.instance.game.dedicated_build
		)
		asyncio.ensure_future(self.initiate_api())

	async def initiate_api(self):
		if not self.api:
			return
		await self.api.on_start()
		try:
			await self.api.authenticate()
			self.ready = True
		except RequestsConnectionError as e:
			logger.error('Can\'t connect to dedimania! Dedimania down or blocked by your host? {}'.format(str(e)))
			self.ready = False
			return
		except ConnectionRefusedError as e:
			logger.error('Can\'t connect to dedimania! Dedimania down or blocked by your host? {}'.format(str(e)))
			self.ready = False
			return
		except DedimaniaInvalidCredentials:
			logger.error('Can\'t connect to dedimania! Code or login is invalid!')
			message = '$f00Error: Your dedimania code or login is invalid!'
			await self.instance.chat(message)
			self.ready = False
			return
		except Exception as e:
			logger.exception(e)
			logger.error('Dedimania app unloaded!')
			print(type(e))
			return

		if self.ready:
			await self.map_begin(self.instance.map_manager.current_map)

	async def show_records_list(self, player, data = None, **kwargs):
		"""
		Show record list view to player.

		:param player: Player instance.
		:param data: -
		:param kwargs: -
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: view instance or nothing when there are no records.
		"""
		if not len(self.current_records):
			message = '$i$f00There are currently no dedimania records on this map!'
			await self.instance.chat(message, player)
			return

		# TODO: Move logic to view class.
		index = 1
		view = DedimaniaRecordsListView(self)
		view_data = []

		async with self.lock:
			first_time = self.current_records[0].score
			for item in self.current_records:
				record_time_difference = ''
				if index > 1:
					record_time_difference = '$f00 + ' + times.format_time((item.score - first_time))
				view_data.append({'index': index, 'nickname': item.nickname,
								  'record_time': times.format_time(item.score),
								  'record_time_difference': record_time_difference})
				index += 1
		view.objects_raw = view_data
		view.title = 'Dedimania Records on {}'.format(self.instance.map_manager.current_map.name)
		await view.display(player=player.login)
		return view

	async def map_start(self, map, restarted, **kwargs):
		if restarted:
			# TODO: Activate after fix in dedicated:
			# await self.podium_start()

			# Clear the current map.
			self.map_uid = None

			await self.map_end(map)
			await self.map_begin(map)

	async def map_begin(self, map, **kwargs):
		# Reset.
		if not self.api:
			await self.reload_settings()
			await self.initiate_api()
		if not self.api:
			return

		self.api.retries = 0

		# If the map uid already has been filled and the same we are starting double. Return immediately.
		# This is because of issue #276.
		if self.map_uid == self.instance.map_manager.current_map.uid:
			return
		self.map_uid = self.instance.map_manager.current_map.uid

		# Set map status.
		self.map_status = map.author_login == 'nadeo' or map.time_author > 6200 and map.num_checkpoints > 1
		if not self.map_status:
			message = '$f90This map is not supported by Dedimania (min 1 checkpoint + 6.2 seconds or higher author time).'
			await self.widget.hide()
			return await self.instance.chat(message)

		# Refresh script.
		self.current_script = (await self.instance.mode_manager.get_current_script()).lower()

		# Fetch records + update widget.
		async with self.lock:
			self.v_replay = None
			self.v_replay_checks = None
			self.ghost_replay = None
			self.current_records = list()
		if self.ready:
			await self.widget.display()

		await self.refresh_records()

		if self.ready:
			await asyncio.gather(
				self.chat_current_record(),
				self.widget.display()
			)

	async def podium_start(self, force=False, **kwargs):
		# Get replays of the players.
		self.v_replay = None
		self.v_replay_checks = None

		# TODO: Remove if statement after fix dedicated.
		if not force:
			self.ghost_replay = None

		# TODO: Remove this block after fix dedicated.
		if force:
			self.v_replay = None
			self.v_replay_checks = None

		async with self.lock:
			for pos, record in enumerate(self.current_records):
				if record.updated:
					if not self.v_replay:
						replay = await self.get_v_replay(record.login)
						if replay:
							self.v_replay = replay
					if not self.v_replay_checks and self.current_script.startswith('Laps'):
						self.v_replay_checks = ','.join([str(c) for c in record.race_cps])

					if pos == 0:
						replay = await self.get_ghost_replay(record.login)
						if replay:
							self.ghost_replay = replay

	async def map_end(self, map):
		if self.map_status is False:
			logger.warning('Don\'t send dedi records, map not supported!')
			return

		if not self.v_replay:
			return

		async with self.lock:
			try:
				logger.debug('Sending Dedimania times...')
				await self.api.set_map_times(
					map, self.current_script, self.current_records.copy(), self.v_replay, self.v_replay_checks, self.ghost_replay,
				)
				if await self.setting_sent_announce.get_value():
					await self.instance.chat(
						'$0b3Dedimania records has been sent successfully!'
					)
			except DedimaniaNotSupportedException:
				pass
			except (DedimaniaTransportException, DedimaniaFault) as e:
				logger.error(e)
				if 'session' not in str(e):
					message = '$f00Error: Dedimania got an error, didn\'t send records :( (Error: {})'.format(str(e))
					await self.instance.chat(message)

	async def refresh_records(self):
		try:
			player_list, self.current_script = await asyncio.gather(
				self.instance.gbx('GetPlayerList', -1, 0),
				self.instance.mode_manager.get_current_script(),
			)
			self.server_max_rank, modes, player_infos, self.current_records = await self.api.get_map_details(
				self.instance.map_manager.current_map,
				self.current_script,
				server_name=self.instance.game.server_name, server_comment='', is_private=self.instance.game.server_is_private,
				max_players=self.instance.game.server_max_players, max_specs=self.instance.game.server_max_specs,
				players=player_list,
				server_login=self.instance.game.server_player_login
			)
			self.ready = True
		except DedimaniaNotSupportedException as e:
			self.ready = False
			await self.instance.chat('$0b3Dedimania doesn\'t support or know the current script mode {}'.format(
				self.current_script
			))
			logger.warning('Dedimania doesn\'t support or known the mode {}'.format(self.current_script))

			# Still silently report.
			handle_exception(e, module_name=__name__, func_name='refresh_records', extra_data={
				'script': self.current_script
			})
			return
		except DedimaniaTransportException as e:
			self.ready = False

			if 'Max retries exceeded' in str(e):
				message = '$f00Error: Dedimania seems down?'
			else:
				message = '$f00Error: Dedimania error occured!'
				logger.exception(e)
			await self.instance.chat(message)
			return
		except DedimaniaFault as e:
			self.ready = False

			if 'session' in str(e).lower():
				handle_exception(e, module_name=__name__, func_name='refresh_records')
			logger.error('Dedimania gave an Fault: {}'.format(str(e)))

			self.current_records = list()
			return
		except Exception as e:
			self.ready = False
			handle_exception(e, module_name=__name__, func_name='refresh_records')
			logger.exception(e)
			self.current_records = list()
			return

		for info in player_infos:
			self.player_info[info['Login']] = dict(
				banned=False, login=info['Login'], max_rank=info['MaxRank'],
			)

	async def player_connect(self, player, is_spectator, **kwargs):
		try:
			if not self.api:
				return
			if self.ready:
				await self.widget.display(player=player)
			res = await self.instance.gbx('GetDetailedPlayerInfo', player.login)
			p_info = await self.api.player_connect(
				player.login, player.nickname, res['Path'], is_spectator
			)
			if p_info:
				self.player_info[player.login] = p_info
		except ConnectionRefusedError:
			return
		except TimeoutError:
			return
		except DedimaniaException:
			return

	async def player_disconnect(self, player, **kwargs):
		try:
			del self.player_info[player.login]
		except:
			pass
		try:
			if not self.api:
				return
			await self.api.player_disconnect(player.login, '')
		except:
			pass

	async def player_finish(self, player, race_time, lap_time, lap_cps, race_cps, flow, raw, **kwargs):
		if not self.map_status:
			return
		if not self.ready:
			return
		if player.login not in self.player_info:
			logger.warning('Player info not (yet) retrieved from dedimania for the player {}'.format(player.login))
			return
		player_info = self.player_info[player.login]
		chat_announce = await self.setting_chat_announce.get_value()
		current_records = [x for x in self.current_records if x.login == player.login]
		score = lap_time
		if len(current_records) > 0:
			current_record = current_records[0]
			previous_index = self.current_records.index(current_record) + 1

			if score < current_record.score:
				previous_time = current_record.score
				current_record.updated = True
				if self.current_script.startswith('Laps'):
					current_record.race_cps = race_cps

				# Determinate new rank.
				async with self.lock:
					new_rank = 1
					for idx, record in enumerate(self.current_records):
						new_rank = idx + 1
						if score <= record.score:
							break

				# Check if the player or server allows this player to finish with his max_rank.
				if new_rank > int(self.server_max_rank) and new_rank > int(player_info['max_rank']):
					logger.debug('Ignore time, not within server or player max_rank.')
					return

				# Update score + infos.
				async with self.lock:
					current_record.score = score
					current_record.cps = lap_cps
					self.current_records.sort(key=lambda x: x.score)

				if new_rank < previous_index:
					message = '$fff{}$z$s$0b3 gained the $fff{}.$0b3 Dedimania Record: $fff\uf017 {}$0b3 ($fff{}.$0b3 $fff-{}$0b3).'.format(
						player.nickname, new_rank, times.format_time(score), previous_index,
						times.format_time((previous_time - score))
					)
				else:
					message = '$fff{}$z$s$0b3 improved the $fff{}.$0b3 Dedimania Record: $fff\uf017 {}$0b3 ($fff-{}$0b3).'.format(
						player.nickname, new_rank, times.format_time(score),
						times.format_time((previous_time - score))
					)

				coros = [self.widget.display()]

				# TODO: Temp fix for dedicated bug
				coros.append(self.podium_start(force=True))
				# END TEMP FIX

				if chat_announce >= new_rank:
					coros.append(self.instance.chat(message))
				elif chat_announce != 0:
					coros.append(self.instance.chat(message, player))
				await asyncio.gather(*coros)

			elif score == current_record.score:
				message = '$fff{}$z$s$0b3 equalled the $fff{}.$0b3 Dedimania Record: $fff\uf017 {}$0b3.'.format(
					player.nickname, previous_index, times.format_time(score)
				)

				if chat_announce >= previous_index:
					return await self.instance.chat(message)
				elif chat_announce != 0:
					return await self.instance.chat(message, player)

		else:
			new_record = DedimaniaRecord(
				login=player.login, nickname=player.nickname, score=score, rank=None, max_rank=player_info['max_rank'],
				cps=lap_cps, vote=-1
			)
			new_record.updated = True
			if self.current_script.startswith('Laps'):
				new_record.race_cps = race_cps

			# Determinate new rank.
			async with self.lock:
				new_rank = 1
				for idx, record in enumerate(self.current_records):
					new_rank = idx + 1
					if score <= record.score:
						break

			# Check if the player or server allows this player to finish with his max_rank.
			if new_rank > int(self.server_max_rank) and new_rank > int(player_info['max_rank']):
				logger.debug('Ignore time, not within server or player max_rank.')
				return

			async with self.lock:
				self.current_records.append(new_record)
				self.current_records.sort(key=lambda x: x.score)
				new_index = self.current_records.index(new_record) + 1
			message = '$fff{}$z$s$0b3 drove the $fff{}.$0b3 Dedimania Record: $fff\uf017 {}$0b3.'.format(
				player.nickname, new_index, times.format_time(score)
			)
			await asyncio.gather(
				self.instance.chat(message),
				self.widget.display(),

				# TODO: Temp fix for dedicated bug
				self.podium_start(force=True)
				# END TEMP FIX.
			)

	async def get_v_replay(self, login):
		try:
			return await self.instance.gbx('GetValidationReplay', login)
		except:
			return None

	async def get_ghost_replay(self, login):
		replay_name = 'dedimania_{}.Replay.Gbx'.format(uuid.uuid4().hex)
		try:
			await self.instance.gbx('SaveBestGhostsReplay', login, replay_name)
		except:
			return None
		try:
			async with self.instance.storage.open('UserData/Replays/{}'.format(replay_name)) as ghost_file:
				return await ghost_file.read()
		except FileNotFoundError as e:
			message = '$f00Error: Dedimania requires you to have file access on the server. We can\'t fetch' \
					  'the driven replay!'
			logger.error('Please make sure we can access the dedicated files. Configure your storage driver correctly! '
						 '{}'.format(str(e)))
			await self.instance.chat(message)
			raise DedimaniaException('Can\'t access replay file')
		except PermissionError as e:
			message = '$f00Error: Dedimania requires you to have file access on the server. We can\'t fetch' \
					  'the driven replay because of an permission problem!'
			logger.error('We can\'t read files in the dedicated folder, your permissions don\'t allow us to read it! '
						 '{}'.format(str(e)))
			await self.instance.chat(message)
			raise DedimaniaException('Can\'t access files due to permission problems')

	async def chat_current_record(self):
		records_amount = len(self.current_records)
		if records_amount > 0:
			first_record = self.current_records[0]
			message = '$0b3Current Dedimania Record: $fff\uf017 {}$z$s$0b3 by $fff{}$z$s$0b3 ($fff{}$0b3 records)'.format(
				times.format_time(first_record.score), first_record.nickname, records_amount
			)
			calls = list()
			calls.append(self.instance.chat(message))

			for player in self.instance.player_manager.online:
				calls.append(await self.chat_personal_record(player))
			return await asyncio.gather(*calls)
		else:
			message = '$0b3There is no Dedimania Record on this map yet.'
			return await self.instance.chat(message)

	async def chat_personal_record(self, player):
		async with self.lock:
			record = [x for x in self.current_records if x.login == player.login]

		if len(record) > 0:
			message = '$0b3You currently hold the $fff{}.$0b3 Dedimania Record: $fff\uf017 {}'.format(
				self.current_records.index(record[0]) + 1, times.format_time(record[0].score)
			)
			return self.instance.chat(message, player)
		else:
			message = '$0b3You don\'t have a Dedimania Record on this map yet.'
			return self.instance.chat(message, player)
