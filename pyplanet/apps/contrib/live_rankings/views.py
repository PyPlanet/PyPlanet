import math

from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.utils import times


class LiveRankingsWidget(TimesWidgetView):
	widget_x = -161
	widget_y = 55.5
	size_x = 38
	size_y = 55.5
	top_entries = 5
	title = None  # 'Live Rankings'
	icon_style = 'BgRaceScore2'
	icon_substyle = 'LadderRank'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_liverankings'

		self.record_amount = math.floor((self.size_y - 5.5) / 3.3)
		self.format_times = True

	async def get_player_data(self):
		data = await super().get_player_data()
		widget_times = dict()

		for player in self.app.instance.player_manager.online:
			list_records = list()

			player_record = [x for x in self.app.current_rankings if x['nickname'] == player.nickname]
			player_index = (len(self.app.current_rankings) + 1)
			if len(player_record) > 0:
				# Set player index if there is a record
				player_index = (self.app.current_rankings.index(player_record[0]) + 1)

			records = list(self.app.current_rankings[:self.top_entries])
			custom_start_index = None
			if player_index > len(self.app.current_rankings):
				# No personal record, get the last records
				records_start = (len(self.app.current_rankings) - self.record_amount + self.top_entries)
				# If start of current slice is in the top entries, add more records below
				if records_start < self.top_entries:
					records_start = (self.top_entries)

				records += list(self.app.current_rankings[records_start:])
				custom_start_index = (records_start + 1)
			else:
				if player_index <= self.top_entries:
					# Player record is in top X, get following records (top entries + 1 onwards)
					records += self.app.current_rankings[(self.top_entries + 1):(self.record_amount + 1)]
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
			for record in records:
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
				if index == self.top_entries:
					index = custom_start_index
				else:
					index += 1
				list_records.append(list_record)

			widget_times[player.login] = {'times': list_records}

		data.update(widget_times)

		return data
