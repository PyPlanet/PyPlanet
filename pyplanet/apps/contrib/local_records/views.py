import math

from pyplanet.utils.style import style_strip
from pyplanet.utils.times import format_time
from pyplanet.views.generics import ask_confirmation
from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.views.generics.list import ManualListView
from pyplanet.utils import times


class LocalRecordsWidget(TimesWidgetView):
	widget_x = 125
	widget_y = 56.5
	top_entries = 5
	title = 'Local Records'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_localrecords'

		self.action = self.action_recordlist
		self.record_amount = 15

	async def get_player_data(self):
		data = await super().get_player_data()
		if self.app.instance.performance_mode:
			return data

		record_limit = await self.app.setting_record_limit.get_value()
		if record_limit > 0:
			current_records = self.app.current_records[:record_limit]
		else:
			current_records = self.app.current_records
		widget_times = dict()

		for player in self.app.instance.player_manager.online:
			list_records = list()

			player_record = [x for x in current_records if x.player_id == player.get_id()]
			player_index = (len(current_records) + 1)
			if len(player_record) > 0:
				# Set player index if there is a record
				player_index = (current_records.index(player_record[0]) + 1)

			records = list(current_records[:self.top_entries])
			custom_start_index = None
			if player_index > len(current_records):
				# No personal record, get the last records
				records_start = (len(current_records) - self.record_amount + self.top_entries)
				# If start of current slice is in the top entries, add more records below
				if records_start < self.top_entries:
					records_start = (self.top_entries)

				records += list(current_records[records_start:])
				custom_start_index = (records_start + 1)
			else:
				if player_index <= self.top_entries:
					# Player record is in top X, get following records (top entries + 1 onwards)
					records += current_records[self.top_entries:self.record_amount]
					custom_start_index = (self.top_entries + 1)
				else:
					# Player record is not in top X, get records around player record
					# Same amount above the record as below, except when not possible (favors above)
					records_to_fill = (self.record_amount - self.top_entries)
					start_point = ((player_index - math.ceil((records_to_fill - 1) / 2)) - 1)
					end_point = ((player_index + math.floor((records_to_fill - 1) / 2)) - 1)

					# If end of current slice is outside the list, add more records above
					if end_point > len(current_records):
						end_difference = (end_point - len(current_records))
						start_point = (start_point - end_difference)
					# If start of current slice is in the top entries, add more records below
					if start_point < self.top_entries:
						start_point = self.top_entries

					records += current_records[start_point:(start_point + records_to_fill)]
					custom_start_index = (start_point + 1)

			index = 1
			for record in records:
				record_player = await record.get_related('player')
				list_record = dict()
				list_record['index'] = index
				list_record['color'] = '$fff'
				if index <= self.top_entries:
					list_record['color'] = '$ff0'
				if index == player_index:
					list_record['color'] = '$0f3'
				list_record['nickname'] = record_player.nickname
				list_record['score'] = times.format_time(int(record.score))
				if index == self.top_entries:
					index = custom_start_index
				else:
					index += 1
				list_records.append(list_record)

			widget_times[player.login] = {'times': list_records}

		data.update(widget_times)

		return data

	async def get_context_data(self):
		context = await super().get_context_data()

		# Add facts.
		context.update({
			'top_entries': self.top_entries
		})

		record_limit = await self.app.setting_record_limit.get_value()
		if record_limit > 0:
			current_records = self.app.current_records[:record_limit]
		else:
			current_records = self.app.current_records

		if self.app.instance.performance_mode:
			list_records = list()
			records = list(current_records[:self.record_amount])

			index = 1
			for record in records:
				record_player = await record.get_related('player')
				list_record = dict()
				list_record['index'] = index
				list_record['color'] = '$fff'
				if index <= self.top_entries:
					list_record['color'] = '$ff0'
				list_record['nickname'] = record_player.nickname
				list_record['score'] = times.format_time(int(record.score))
				index += 1
				list_records.append(list_record)

			context.update({
				'times': list_records
			})

		return context

	async def action_recordlist(self, player, **kwargs):
		await self.app.show_records_list(player)


class LocalRecordsListView(ManualListView):
	title = 'Local Records on this map'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	fields = [
		{
			'name': '#',
			'index': 'index',
			'sorting': True,
			'searching': False,
			'width': 10,
			'type': 'label'
		},
		{
			'name': 'Player',
			'index': 'player_nickname',
			'sorting': False,
			'searching': True,
			'width': 70
		},
		{
			'name': 'Time',
			'index': 'record_time',
			'sorting': True,
			'searching': False,
			'width': 30,
			'type': 'label'
		},
		{
			'name': 'Difference',
			'index': 'record_time_difference',
			'sorting': True,
			'searching': False,
			'width': 50,
			'type': 'label'
		},
	]

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui

	async def get_title(self):
		return 'Local Records on {}'.format(self.app.instance.map_manager.current_map.name)

	async def get_data(self):
		first_time = self.app.current_records[0].score if len(self.app.current_records) > 0 else None
		record_limit = await self.app.setting_record_limit.get_value()
		if record_limit > 0:
			records = self.app.current_records[:record_limit]
		else:
			records = self.app.current_records

		index = 1
		items = []
		for item in records:
			record_player = item.player
			record_time_difference = ''
			if index > 1:
				record_time_difference = '$f00 + ' + times.format_time((item.score - first_time))
			items.append({
				'id': item.get_id(),
				'index': index, 'player_nickname': record_player.nickname,
				'record_time': times.format_time(item.score),
				'record_time_difference': record_time_difference
			})
			index += 1

		return items

	async def get_actions(self):
		return [
			dict(
				name='Delete record',
				action=self.delete_record,
				text='&#xf1f8;',
				textsize='1.2',
				safe=True,
				type='label',
				order=49,
				require_confirm=False,
			)
		]

	async def delete_record(self, player, values, data, view, **kwargs):
		if not await self.app.instance.permission_manager.has_permission(player, 'local_records:manage_records'):
			return await self.app.instance.chat('$ff0You do not have permissions to manage local records!')

		try:
			record = await self.app.get_local(id=data['id'])
		except:
			return

		if not await ask_confirmation(player, 'Are you sure you want to remove record {} by {}'.format(
			format_time(record.score), style_strip((await record.get_related('player')).nickname)
		), size='sm'):
			await self.app.delete_record(record)
			await self.app.refresh()
			await self.refresh(player)


class LocalRecordCpCompareListView(ManualListView):
	title = 'Local Record checkpoint comparison'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, own_record, own_rank, compare_record, compare_rank):
		"""
		Init compare listview.

		:param app: App instance
		:param own_record: Own record
		:param own_rank: Own rank number
		:param compare_record: Compare with record.
		:param compare_rank: Compare rank number
		:type own_record: pyplanet.apps.contrib.local_records.models.local_record.LocalRecord
		:type compare_record: pyplanet.apps.contrib.local_records.models.local_record.LocalRecord
		"""
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.provide_search = False

		self.own_record = own_record
		self.own_rank = own_rank
		self.compare_record = compare_record
		self.compare_rank = compare_rank

	async def get_fields(self):
		own_player = await self.own_record.get_related('player')
		compare_player = await self.compare_record.get_related('player')

		return [
			{
				'name': 'Checkpoint',
				'index': 'cp',
				'sorting': False,
				'searching': False,
				'width': 40,
				'type': 'label'
			},
			{
				'name': '#{}: $n{}'.format(self.own_rank, style_strip(own_player.nickname)),
				'index': 'own_time',
				'sorting': False,
				'searching': False,
				'width': 70
			},
			{
				'name': '#{}: $n{}'.format(self.compare_rank, style_strip(compare_player.nickname)),
				'index': 'compare_time',
				'sorting': False,
				'searching': False,
				'width': 70,
			},
			{
				'name': 'Difference',
				'index': 'difference',
				'sorting': False,
				'searching': False,
				'width': 50,
				'type': 'label'
			},
		]

	async def get_title(self):
		return 'Local Record CP comparison on {}'.format(self.app.instance.map_manager.current_map.name)

	def get_diff_text(self, a, b):
		diff = a - b
		diff_prefix = '$FFF'
		if diff > 0:
			diff_prefix = '$F66+'  # Red
		elif diff < 0:
			diff_prefix = '$6CF- '  # Blue

		return '{}{}'.format(diff_prefix, format_time(abs(diff)))

	async def get_data(self):
		own_cps = [int(c) for c in self.own_record.checkpoints.split(',')]
		compare_cps = [int(c) for c in self.compare_record.checkpoints.split(',')]
		total_cps = len(own_cps)

		data = list()
		for cp, (own, compare) in enumerate(zip(own_cps, compare_cps)):
			data.append(dict(
				cp='Finish' if (cp + 1) == total_cps else cp + 1,
				own_time=format_time(own),
				compare_time=format_time(compare),
				difference=self.get_diff_text(own, compare)
			))

		return data
