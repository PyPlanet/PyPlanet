import math

from pyplanet.utils.style import style_strip
from pyplanet.utils.times import format_time
from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.views.generics.list import ManualListView
from pyplanet.utils import times


class DedimaniaRecordsWidget(TimesWidgetView):
	widget_x = -160
	widget_y = 70.5
	z_index = 130
	size_x = 38
	size_y = 55.5
	top_entries = 5
	title = 'Dedimania'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_dedimaniarecords'

		self.action = self.action_recordlist
		self.record_amount = 15

	async def get_player_data(self):
		data = await super().get_player_data()
		if self.app.instance.performance_mode:
			return data

		widget_times = dict()

		for player in self.app.instance.player_manager.online:
			player_record = [x for x in self.app.current_records if x.login == player.login]
			player_index = (len(self.app.current_records) + 1)
			list_records = list()
			if len(player_record) > 0:
				# Set player index if there is a record
				player_index = (self.app.current_records.index(player_record[0]) + 1)

			records = list(self.app.current_records[:self.top_entries])
			custom_start_index = None
			if player_index > len(self.app.current_records):
				# No personal record, get the last records
				records_start = (len(self.app.current_records) - self.record_amount + self.top_entries)
				# If start of current slice is in the top entries, add more records below
				if records_start < self.top_entries:
					records_start = self.top_entries

				records += list(self.app.current_records[records_start:])
				custom_start_index = (records_start + 1)
			else:
				if player_index <= self.top_entries:
					# Player record is in top X, get following records (top entries + 1 onwards)
					records += self.app.current_records[self.top_entries:self.record_amount]
					custom_start_index = (self.top_entries + 1)
				else:
					# Player record is not in top X, get records around player record
					# Same amount above the record as below, except when not possible (favors above)
					records_to_fill = (self.record_amount - self.top_entries)
					start_point = ((player_index - math.ceil((records_to_fill - 1) / 2)) - 1)
					end_point = ((player_index + math.floor((records_to_fill - 1) / 2)) - 1)

					# If end of current slice is outside the list, add more records above
					if end_point > len(self.app.current_records):
						end_difference = (end_point - len(self.app.current_records))
						start_point = (start_point - end_difference)
					# If start of current slice is in the top entries, add more records below
					if start_point < self.top_entries:
						start_point = self.top_entries

					records += self.app.current_records[start_point:(start_point + records_to_fill)]
					custom_start_index = (start_point + 1)

			index = 1
			for record in records:
				list_record = dict()
				list_record['index'] = index
				list_record['color'] = '$fff'
				if index <= self.top_entries:
					list_record['color'] = '$ff0'
				if index == player_index:
					list_record['color'] = '$0f3'
				list_record['nickname'] = record.nickname
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

		if self.app.instance.performance_mode:
			list_records = list()
			records = list(self.app.current_records[:self.record_amount])

			index = 1
			for record in records:
				list_record = dict()
				list_record['index'] = index
				list_record['color'] = '$fff'
				if index <= self.top_entries:
					list_record['color'] = '$ff0'
				list_record['nickname'] = record.nickname
				list_record['score'] = times.format_time(int(record.score))
				index += 1
				list_records.append(list_record)

			context.update({
				'times': list_records
			})

		return context

	async def action_recordlist(self, player, **kwargs):
		await self.app.show_records_list(player)


class DedimaniaRecordsListView(ManualListView):
	title = 'Dedimania Records on this map'
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
			'index': 'nickname',
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
		return 'Dedimania Records on $l[http://dedimania.net/tm2stats/?do=stat&UId={}&Show=RECORDS]{}$l'.format(
			self.app.instance.map_manager.current_map.uid, self.app.instance.map_manager.current_map.name
		)

	async def get_data(self):
		index = 1
		items = []
		async with self.app.lock:
			first_time = self.app.current_records[0].score
			for item in self.app.current_records:
				record_time_difference = ''
				if index > 1:
					record_time_difference = '$f00 + ' + times.format_time((item.score - first_time))
				items.append({
					'index': index, 'nickname': item.nickname,
					'record_time': times.format_time(item.score),
					'record_time_difference': record_time_difference
				})
				index += 1

		return items


class DedimaniaCpCompareListView(ManualListView):
	title = 'Dedimania checkpoint comparison'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app, own_record, compare_record):
		"""
		Init compare listview.

		:param app: App instance
		:param own_record: Own record
		:param compare_record: Compare with record.
		:type own_record: pyplanet.apps.contrib.dedimania.api.DedimaniaRecord
		:type compare_record: pyplanet.apps.contrib.dedimania.api.DedimaniaRecord
		"""
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.provide_search = False

		self.own_record = own_record
		self.compare_record = compare_record

	async def get_fields(self):
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
				'name': '#{}: $n{}'.format(self.own_record.rank, style_strip(self.own_record.nickname)) if self.own_record else '-',
				'index': 'own_time',
				'sorting': False,
				'searching': False,
				'width': 70
			},
			{
				'name': '#{}: $n{}'.format(self.compare_record.rank, style_strip(self.compare_record.nickname)),
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
		return 'Dedimania CP comparison on {}'.format(self.app.instance.map_manager.current_map.name)

	def get_diff_text(self, a, b):
		diff = a - b
		diff_prefix = '$FFF'
		if diff > 0:
			diff_prefix = '$F66+'  # Red
		elif diff < 0:
			diff_prefix = '$6CF- '  # Blue

		return '{}{}'.format(diff_prefix, format_time(abs(diff)))

	async def get_data(self):
		compare_cps = self.compare_record.cps
		own_cps = self.own_record.cps if self.own_record else [None for _ in compare_cps]
		total_cps = len(own_cps)

		data = list()
		for cp, (own, compare) in enumerate(zip(own_cps, compare_cps)):
			data.append(dict(
				cp='Finish' if (cp + 1) == total_cps else cp + 1,
				own_time=format_time(own) if own else '',
				compare_time=format_time(compare),
				difference=self.get_diff_text(own, compare) if self.own_record else '-'
			))

		return data
