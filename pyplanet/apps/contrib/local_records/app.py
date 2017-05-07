from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.local_records.views import LocalRecordsListView, LocalRecordsWidget
from pyplanet.contrib.command import Command

from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.utils import times

from .models import LocalRecord


class LocalRecords(AppConfig):
	name = 'pyplanet.apps.contrib.local_records'
	game_dependencies = ['trackmania']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_records = []
		self.widget = None

	async def on_start(self):
		# Register commands
		await self.instance.command_manager.register(Command(command='records', target=self.show_records_list))

		# Register signals
		self.instance.signal_manager.listen(mp_signals.map.map_begin, self.map_begin)
		self.instance.signal_manager.listen(tm_signals.finish, self.player_finish)
		self.instance.signal_manager.listen(mp_signals.player.player_connect, self.player_connect)

		# Load initial data.
		await self.refresh_locals()
		await self.chat_current_record()

		self.widget = LocalRecordsWidget(self)
		await self.widget.display()

	async def refresh_locals(self):
		record_list = await LocalRecord.objects.execute(
			LocalRecord.select().where(
				LocalRecord.map_id == self.instance.map_manager.current_map.get_id()
			).order_by(LocalRecord.score.asc())
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
			message = '$z$s$fff» $i$f00There are currently no records on this map!'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
			return

		# TODO: Move logic to view class.
		index = 1
		view = LocalRecordsListView(self)
		view_data = []
		first_time = self.current_records[0].score
		for item in self.current_records:
			record_player = await item.get_related('player')
			record_time_difference = ''
			if index > 1:
				record_time_difference = '$f00 + ' + times.format_time((item.score - first_time))
			view_data.append({'index': index, 'player_nickname': record_player.nickname,
							  'record_time': times.format_time(item.score),
							  'record_time_difference': record_time_difference})
			index += 1
		view.objects_raw = view_data
		view.title = 'Local Records on {}'.format(self.instance.map_manager.current_map.name)
		await view.display(player=player.login)
		return view

	async def map_begin(self, map):
		await self.refresh_locals()
		await self.chat_current_record()
		await self.widget.display()

	async def player_connect(self, player, is_spectator, source, signal):
		await self.widget.display(player=player)

	async def player_finish(self, player, race_time, lap_time, cps, flow, raw, **kwargs):
		current_records = [x for x in self.current_records if x.player_id == player.get_id()]
		score = lap_time
		if len(current_records) > 0:
			current_record = current_records[0]
			previous_index = self.current_records.index(current_record) + 1

			if score < current_record.score:
				previous_time = current_record.score

				current_record.score = score
				current_record.checkpoints = ','.join([str(cp) for cp in cps])
				await current_record.save()
				self.current_records.sort(key=lambda x: x.score)

				new_index = self.current_records.index(current_record) + 1

				if new_index < previous_index:
					message = '$z$s$fff»» $fff{}$z$s$0f3 gained the $fff{}.$0f3 Local Record, with a time of $fff\uf017 {}$0f3 ($fff{}.$0f3 $fff-{}$0f3).'.format(
						player.nickname, new_index, times.format_time(score), previous_index,
						times.format_time((previous_time - score))
					)
				else:
					message = '$z$s$fff»» $fff{}$z$s$0f3 improved the $fff{}.$0f3 Local Record, with a time of $fff\uf017 {}$0f3 ($fff-{}$0f3).'.format(
						player.nickname, new_index, times.format_time(score),
						times.format_time((previous_time - score))
					)

				await self.instance.gbx.execute('ChatSendServerMessage', message)
				await self.widget.display()

			elif score == current_record.score:
				message = '$z$s$fff»» $fff{}$z$s$0f3 equalled the $fff{}.$0f3 Local Record, with a time of $fff\uf017 {}$0f3.'.format(
					player.nickname, previous_index, times.format_time(score)
				)
				await self.instance.gbx.execute('ChatSendServerMessage', message)

		else:
			new_record = LocalRecord(
				map=self.instance.map_manager.current_map,
				player=player,
				score=score,
				checkpoints=','.join([str(cp) for cp in cps])
			)
			await new_record.save()

			self.current_records.append(new_record)
			self.current_records.sort(key=lambda x: x.score)
			new_index = self.current_records.index(new_record) + 1

			message = '$z$s$fff»» $fff{}$z$s$0f3 drove the $fff{}.$0f3 Local Record, with a time of $fff\uf017 {}$0f3.'.format(
				player.nickname, new_index, times.format_time(score)
			)
			await self.instance.gbx.execute('ChatSendServerMessage', message)
			await self.widget.display()

	async def chat_current_record(self):
		records_amount = len(self.current_records)
		if records_amount > 0:
			first_record = self.current_records[0]
			message = '$z$s$fff»» $0f3Current Local Record: $fff\uf017 {}$z$s$0f3 by $fff{}$z$s$0f3 ($fff{}$0f3 records)'.format(
				times.format_time(first_record.score), (await first_record.player).nickname, records_amount
			)
			await self.instance.gbx.execute('ChatSendServerMessage', message)

			for player in self.instance.player_manager.online:
				await self.chat_personal_record(player)
		else:
			message = '$z$s$fff»» $0f3There is no Local Record on this map yet.'
			await self.instance.gbx.execute('ChatSendServerMessage', message)

	async def chat_personal_record(self, player):
		record = [x for x in self.current_records if x.player_id == player.get_id()]

		if len(record) > 0:
			message = '$z$s$fff» $0f3You currently hold the $fff{}.$0f3 Local Record: $fff\uf017 {}'.format(
				self.current_records.index(record[0]) + 1, times.format_time(record[0].score)
			)
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
		else:
			message = '$z$s$fff» $0f3You don\'t have a Local Record on this map yet.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
