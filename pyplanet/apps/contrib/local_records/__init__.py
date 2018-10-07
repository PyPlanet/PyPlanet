import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.local_records.views import LocalRecordsListView, LocalRecordsWidget
from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting

from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from pyplanet.utils import times
from pyplanet.utils.log import handle_exception

from .models import LocalRecord


class LocalRecords(AppConfig):
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.lock = asyncio.Lock()

		self.current_records = []
		self.widget = None

		self.setting_chat_announce = Setting(
			'chat_announce', 'Minimum index for chat announce', Setting.CAT_BEHAVIOUR, type=int,
			description='Minimum record index needed for public new record/recordchange announcement (0 for disable).',
			default=50
		)

		self.setting_record_limit = Setting(
			'record_limit', 'Local Records limit', Setting.CAT_BEHAVIOUR, type=int,
			description='Limit for the amount of Local Records displayed in-game (0 for disable).',
			default=100
		)

	async def on_start(self):
		# Register commands
		await self.instance.command_manager.register(
			Command(command='records', target=self.show_records_list),
			Command(
				'localcps', target=self.command_localcps, description='Compare your local record checkpoints with another record.'
			).add_param('record', required=False, type=int, help='Custom record rank to compare with. Defaults to 1.', default=1)
		)

		# Register signals
		self.context.signals.listen(mp_signals.map.map_begin, self.map_begin)
		self.context.signals.listen(tm_signals.finish, self.player_finish)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)

		# Register settings
		await self.context.setting.register(self.setting_chat_announce, self.setting_record_limit)

		# Register permissions
		await self.instance.permission_manager.register('manage_records', 'Manage records', app=self, min_level=3)

		# Load initial data.
		await self.refresh_locals()
		await self.chat_current_record()

		if self.widget is None:
			self.widget = LocalRecordsWidget(self)

		await self.widget.display()

	async def load_map_locals(self, map=None):
		if map:
			map.local = await self.get_map_record(map)
		else:
			maps = {m.id: m for m in self.instance.map_manager.maps}
			map_locals = dict()

			# Fetch all.
			rows = await LocalRecord.execute(
				LocalRecord.select().where(
					LocalRecord.map_id << list(maps.keys())
				)
			)

			# Group by map.
			for row in rows:
				if row.map_id not in map_locals:
					map_locals[row.map_id] = list()
				map_locals[row.map_id].append(row)

			# Map local stats.
			for map_id, local_list in map_locals.items():
				maps[map_id].local = dict(
					record_count=len(local_list),
					first_record=local_list[0] if len(local_list) > 0 else None
				)

			del map_locals
			del maps

	async def get_map_record(self, map=None):
		if not map:
			map = self.instance.map_manager.current_map

		record_list = await LocalRecord.objects.execute(
			LocalRecord.select(LocalRecord, Player)
				.join(Player)
				.where(LocalRecord.map_id == map.get_id())
				.order_by(LocalRecord.score.asc())
		)

		return {
			'record_count': len(record_list),
			'first_record': record_list[0] if len(record_list) > 0 else None
		}

	async def get_player_record_for_map(self, map, player):
		record_list = await LocalRecord.objects.execute(
			LocalRecord.select(LocalRecord)
				.where(LocalRecord.player_id == player.get_id())
				.where(LocalRecord.map_id == map.get_id())
		)

		return record_list

	async def get_player_record_and_rank_for_map(self, map, player):
		record_list = await LocalRecord.objects.execute(
			LocalRecord.select(LocalRecord, Player)
				.join(Player)
				.where(LocalRecord.map_id == map.get_id())
				.order_by(LocalRecord.score.asc())
		)

		rank = 1
		for rec in record_list:
			if rec.player == player:
				return rank, rec
			rank += 1
		return None, None

	async def get_local(self, id):
		return await LocalRecord.get(id=id)

	async def refresh(self):
		await self.refresh_locals()
		if self.widget:
			await self.widget.refresh()

	async def delete_record(self, record):
		await LocalRecord.execute(
			LocalRecord.delete().where(LocalRecord.id == record.get_id())
		)

	async def refresh_locals(self):
		record_list = await LocalRecord.objects.execute(
			LocalRecord.select(LocalRecord, Player)
				.join(Player)
				.where(LocalRecord.map_id == self.instance.map_manager.current_map.get_id())
				.order_by(LocalRecord.score.asc())
		)
		self.current_records = list(record_list)

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
			message = '$i$f00There are currently no records on this map!'
			await self.instance.chat(message, player)
			return

		view = LocalRecordsListView(self)
		await view.display(player=player.login)
		return view

	async def map_begin(self, map):
		await self.refresh_locals()

		if self.widget is None:
			self.widget = LocalRecordsWidget(self)

		await asyncio.gather(
			self.chat_current_record(),
			self.widget.display()
		)

	async def player_connect(self, player, is_spectator, source, signal):
		if self.widget:
			await self.widget.display(player=player)

	async def player_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		record_limit = await self.setting_record_limit.get_value()
		chat_announce = await self.setting_chat_announce.get_value()
		async with self.lock:
			current_records = [x for x in self.current_records if x.player.login == player.login]
			score = lap_time

			previous_index = None
			previous_time = None

			if len(current_records) > 0:
				current_record = current_records[0]
				if score > current_record.score:
					# No improvement, ignore
					return

				# Temporary make index + time local for the messages.
				previous_index = self.current_records.index(current_record) + 1
				previous_time = current_record.score

				# If equal, only show message.
				if score == current_record.score and (record_limit == 0 or previous_index <= record_limit):
					message = '$fff{}$z$s$0f3 equalled the $fff{}.$0f3 Local Record: $fff\uf017 {}$0f3.'.format(
						player.nickname, previous_index, times.format_time(score)
					)

					if chat_announce >= previous_index:
						return await self.instance.chat(message)
					elif chat_announce != 0:
						return await self.instance.chat(message, player.login)

			else:
				current_record = LocalRecord(
					map=self.instance.map_manager.current_map,
					player=player,
				)

			# Set details (score + cps times).
			current_record.score = score
			current_record.checkpoints = ','.join([str(cp) for cp in cps])

			# Add to list when it's a new record!
			if current_record.get_id() is None:
				self.current_records.append(current_record)

			# (Re)sort the record list.
			self.current_records.sort(key=lambda x: x.score)
			new_index = self.current_records.index(current_record) + 1

			if new_index == 1:
				map = next((m for m in self.instance.map_manager.maps if m.uid == self.instance.map_manager.current_map.uid), None)
				if map is not None:
					map.local = {'record_count': len(self.current_records), 'first_record': current_record}

		# Prepare messages.
		if previous_index is not None and (record_limit == 0 or previous_index <= record_limit):
			if new_index < previous_index:
				message = '$fff{}$z$s$0f3 gained the $fff{}.$0f3 Local Record: $fff\uf017 {}$0f3 ($fff{}.$0f3 $fff-{}$0f3).'.format(
					player.nickname, new_index, times.format_time(score), previous_index,
					times.format_time((previous_time - score))
				)
			else:
				message = '$fff{}$z$s$0f3 improved the $fff{}.$0f3 Local Record: $fff\uf017 {}$0f3 ($fff-{}$0f3).'.format(
					player.nickname, new_index, times.format_time(score),
					times.format_time((previous_time - score))
				)
		else:
			message = '$fff{}$z$s$0f3 drove the $fff{}.$0f3 Local Record: $fff\uf017 {}$0f3.'.format(
				player.nickname, new_index, times.format_time(score)
			)

		# Save to database (but don't wait for it).
		try:
			asyncio.ensure_future(current_record.save())
		except Exception as e:
			# To investigate #283.
			handle_exception(e, __name__, 'player_finish', extra_data={
				'own_records': current_records,
				'own_record': current_record
			})

		if self.widget is None:
			self.widget = LocalRecordsWidget(self)

		coros = [self.widget.display()]
		if record_limit == 0 or new_index <= record_limit:
			if chat_announce >= new_index:
				coros.append(self.instance.chat(message))
			elif chat_announce != 0:
				coros.append(self.instance.chat(message, player))
		await asyncio.gather(*coros)

		# Reload map referenced information
		asyncio.ensure_future(self.load_map_locals(map=self.instance.map_manager.current_map))

	async def chat_current_record(self):
		record_limit = await self.setting_record_limit.get_value()
		if record_limit > 0:
			records_amount = len(self.current_records[:record_limit])
		else:
			records_amount = len(self.current_records)

		if records_amount > 0:
			first_record = self.current_records[0]
			message = '$0f3Current Local Record: $fff\uf017 {}$z$s$0f3 by $fff{}$z$s$0f3 ($fff{}$0f3 records)'.format(
				times.format_time(first_record.score), first_record.player.nickname, records_amount
			)
			calls = list()
			calls.append(self.instance.chat(message))
			for player in self.instance.player_manager.online:
				calls.append(self.chat_personal_record(player, record_limit))
			await self.instance.gbx.multicall(*calls)
		else:
			message = '$0f3There is no Local Record on this map yet.'
			await self.instance.chat(message)

	def chat_personal_record(self, player, record_limit):
		if record_limit > 0:
			records = self.current_records[:record_limit]
		else:
			records = self.current_records

		record = [x for x in records if x.player_id == player.get_id()]

		if len(record) > 0:
			message = '$0f3You currently hold the $fff{}.$0f3 Local Record: $fff\uf017 {}'.format(
				self.current_records.index(record[0]) + 1, times.format_time(record[0].score)
			)
			return self.instance.chat(message, player)
		else:
			message = '$0f3You don\'t have a Local Record on this map yet.'
			return self.instance.chat(message, player)

	async def command_localcps(self, player, data, *args, **kwargs):
		"""
		Compare local checkpoints from your record to another record, defaults to 1st record.

		:param player: Player instance
		:param data: Arguments data
		:param args: *
		:param kwargs: **
		:return:
		"""
		async with self.lock:
			record = [x for x in self.current_records if x.player_id == player.get_id()]

			if not len(record):
				message = '$0b3You don\'t have a Local Record on this map yet.'
				return await self.instance.chat(message, player)

			if data.record > len(self.current_records):
				message = '$0b3There is no record for rank {}!'.format(data.record)
				return await self.instance.chat(message, player)

			compare_record = self.current_records[data.record - 1]

			record_index = self.current_records.index(record[0])
			compare_index = self.current_records.index(compare_record)

		view = views.LocalRecordCpCompareListView(self, record[0], record_index, compare_record, compare_index)
		await view.display(player)
