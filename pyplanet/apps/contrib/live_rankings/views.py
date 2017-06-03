import math

from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.utils import times


class LiveRankingsWidget(TimesWidgetView):
	widget_x = -160
	widget_y = 70.5
	size_x = 38
	size_y = 55.5
	top_entries = 5
	title = 'Live Rankings'

	template_name = 'live_rankings/widget.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_liverankings'

		self.record_amount = 15
		self.format_times = True
		self.display_cpdifference = False

	def get_widget_records(self, player=None):
		list_records = list()

		player_index = len(self.app.current_rankings) + 1
		if player:
			player_record = [x for x in self.app.current_rankings if x['nickname'] == player.nickname]
		else:
			player_record = list()

		if len(player_record) > 0:
			# Set player index if there is a record
			player_index = (self.app.current_rankings.index(player_record[0]) + 1)

		records = list(self.app.current_rankings[:self.top_entries])
		if player_index > len(self.app.current_rankings):
			# No personal record, get the last records
			records_start = (len(self.app.current_rankings) - self.record_amount + self.top_entries)
			# If start of current slice is in the top entries, add more records below
			if records_start < self.top_entries:
				records_start = self.top_entries

			records += list(self.app.current_rankings[records_start:])
			custom_start_index = (records_start + 1)
		else:
			if player_index <= self.top_entries:
				# Player record is in top X, get following records (top entries + 1 onwards)
				records += self.app.current_rankings[self.top_entries:self.record_amount]
				custom_start_index = (self.top_entries + 1)
			else:
				# Player record is not in top X, get records around player record
				# Same amount above the record as below, except when not possible (favors above)
				records_to_fill = (self.record_amount - self.top_entries)
				start_point = ((player_index - math.ceil((records_to_fill - 1) / 2)) - 1)
				end_point = ((player_index + math.floor((records_to_fill - 1) / 2)) - 1)

				# If end of current slice is outside the list, add more records above
				if end_point > len(self.app.current_rankings):
					end_difference = (end_point - len(self.app.current_rankings))
					start_point = (start_point - end_difference)
				# If start of current slice is in the top entries, add more records below
				if start_point < self.top_entries:
					start_point = self.top_entries

				records += self.app.current_rankings[start_point:(start_point + records_to_fill)]
				custom_start_index = (start_point + 1)

		index = 1
		best = None
		for record in records:
			if self.display_cpdifference and index == 1:
				best = record

			list_record = dict()
			list_record['index'] = index

			list_record['color'] = '$fff'
			if index < player_index:
				list_record['color'] = '$f00'
			if index <= self.top_entries:
				list_record['color'] = '$ff0'
			if index > player_index:
				list_record['color'] = '$bbb'
			if index == player_index:
				list_record['color'] = '$0f3'

			list_record['nickname'] = record['nickname']

			if self.format_times:
				list_record['score'] = times.format_time(int(record['score']))
			else:
				list_record['score'] = int(record['score'])

			if self.display_cpdifference:
				list_record['cp_difference'] = (best['cps'] - record['cps'])

				if index > 1 and not record['finish']:
					# Calculate difference to first player
					best_cp = best['cp_times'][(record['cps'] - 1)]
					current_diff = (record['score'] - best['cp_times'][(record['cps'] - 1)])
					list_record['score'] = '+ ' + times.format_time(int(current_diff))

				if record['finish']:
					list_record['score'] = '$i' + str(list_record['score'])
				elif record['giveup']:
					list_record['score'] = '$iDNF'
			else:
				list_record['cp_difference'] = None

			if index == self.top_entries:
				index = custom_start_index
			else:
				index += 1

			list_records.append(list_record)
		return list_records

	async def get_context_data(self):
		current_script = await self.app.instance.mode_manager.get_current_script()
		if 'TimeAttack' in current_script:
			self.format_times = True
			self.display_cpdifference = False
		elif 'Laps' in current_script:
			self.format_times = True
			self.display_cpdifference = True
		else:
			self.format_times = False
			self.display_cpdifference = False

		data = await super().get_context_data()
		if self.app.instance.performance_mode:
			data['times'] = self.get_widget_records()
		return data

	async def get_player_data(self):
		data = await super().get_player_data()

		# If in performance mode, ignore this method.
		if self.app.instance.performance_mode:
			return dict()
		else:
			for player in self.app.instance.player_manager.online:
				data[player.login] = dict(times=self.get_widget_records(player))
			return data
