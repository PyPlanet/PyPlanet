import asyncio
import math

from pyplanet.utils import times
from pyplanet.views.generics.widget import WidgetView, TimesWidgetView
from pyplanet.views import TemplateView
from pyplanet.views.generics import ManualListView

class TimerView(WidgetView):
	widget_x = 0
	widget_y = 0
	size_x = 0
	size_y = 0
	template_name = 'nightcup/timer.xml'

	def __init__(self, app):
		super().__init__()
		self.app = app
		self.manager = app.context.ui

class SettingsListView(ManualListView):
	title = 'NightCup settings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'ProfileAdvanced'

	def __init__(self, app, player):
		super().__init__()
		self.manager = app.context.ui
		self.app = app
		self.player = player
		self.sort_field = {
			'name': 'Name',
			'index': 'name',
			'sorting': True,
			'searching': True,
			'width': 60,
			'type':'label'
		}

		self.child = None

	async def get_data(self):
		return await self.app.get_long_settings()

	async def open_edit_setting(self, player, values, row, **kwargs):
		if self.child:
			return

		# Show edit view.
		self.child = NcSettingEditView(self, self.player, row)
		await self.child.display()
		await self.child.wait_for_response()
		await self.child.destroy()
		await self.display()  # refresh.
		self.child = None

	async def display(self, **kwargs):
		# kwargs['player'] = self.player
		return await super().display(self.player)

	def value_renderer(self, row, field, **kwargs):
		value_type = type(row[field['index']])
		if row[field['index']] is None:
			return '-'
		if value_type == str or value_type == int or value_type == float or value_type == bool:
			return str(row[field['index']])
		elif value_type == dict:
			return 'Dictionary, edit to show'
		elif value_type == set or value_type == list:
			return '{} values, edit to show'.format(len(row[field['index']]))
		return 'Unknown type {}'.format(str(value_type))

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 60,
				'type': 'label'
			},
			{
				'name': 'Description',
				'index': 'description',
				'sorting': False,
				'searching': True,
				'width': 75,
				'type': 'label',
			},
			{
				'name': 'Value or contents',
				'index': 'value',
				'sorting': False,
				'searching': False,
				'width': 70,
				'type': 'label',
				'renderer': self.value_renderer,
				'action': self.open_edit_setting
			},
		]

	async def get_actions(self):
		return [
			{
				'name': 'Edit',
				'type': 'label',
				'text': '$fff &#xf040; Edit',
				'width': 11,
				'action': self.open_edit_setting,
				'safe': True
			},
		]

class NcSettingEditView(TemplateView):
	template_name = 'admin/setting/edit.xml'

	def __init__(self, parent, player, setting):
		super().__init__(parent.manager)
		self.parent = parent
		self.player = player
		self.setting = setting

		self.response_future = asyncio.Future()

		self.subscribe('button_close', self.close)
		self.subscribe('button_save', self.save)
		self.subscribe('button_cancel', self.close)

	async def display(self, **kwargs):
		await super().display(player_logins=[self.player.login])

	async def get_context_data(self):
		context = await super().get_context_data()
		context['title'] = 'Edit \'{}\''.format(self.setting['name'])
		context['icon_style'] = 'Icons128x128_1'
		context['icon_substyle'] = 'ProfileAdvanced'

		context['setting'] = self.setting
		context['setting_value'] = self.setting['value']
		context['types'] = dict(int=int, str=str, float=float, set=set, dict=dict, list=list, bool=bool)

		return context

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])
		self.response_future.set_result(None)
		self.response_future.done()

	async def wait_for_response(self):
		return await self.response_future

	async def save(self, player, action, values, *args, **kwargs):
		value = values['setting_value_field']


		try:
			if self.setting['name'] in ['nc_time_until_ta', 'nc_time_until_ko']:
				if int(value) < 5 and int(value) != 0 and int(value) != -1:
					message = '$i$f00Time can not be shorter than 5 seconds.'
					await self.parent.app.instance.chat(message, player)
					return
			if self.setting['name'] == 'nc_ta_length':
				if int(value) < 0:
					message = '$i$f00TA length cannot be negative.'
					await self.parent.instance.chat(message, player)
					return
			settings_long = (await self.parent.get_data())
			settings = {setting['name']: setting['value'] for setting in settings_long}
			settings[self.setting['name']] = type(settings[self.setting['name']])(value)
			await self.parent.app.update_settings(settings)
		except ValueError:
			message = '$i$f00You have entered a value with a wrong type.'
			await self.parent.app.instance.chat(message, player)
			return
		finally:
			await asyncio.gather(
				self.parent.app.instance.chat(
					'$ff0Changed nightcup setting "$fff{}$ff0" to "$fff{}$ff0" (was: "$fff{}$ff0").'.format(
						self.setting['name'], value, self.setting['value']
					),
					player
				),
				self.hide([player.login])
			)
			self.response_future.set_result(self.setting)
			self.response_future.done()

class NcStandingsWidget(TimesWidgetView):
	widget_x = -160
	widget_y = 70.5
	top_entries = 5
	z_index = 30
	size_x = 38
	size_y = 55.5
	title = 'Current CPs'

	template_name = 'nightcup/ncstandings.xml'

	def __init__(self, app, manager):
		super().__init__(self)
		self.app = app
		self.standings_manager = manager
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_nightcupstandings'

		self.record_amount = 30

	async def get_all_player_data(self, logins):
		data = await super().get_all_player_data(logins)

		max_n = math.floor((self.size_y - 5.5) / 3.3)

		scores = {}
		if not self.app.ta_active:
			for player in self.app.instance.player_manager.online:
				last_fin = 0
				list_times = []
				n = 1
				for pcp in self.standings_manager.player_cps:
					# Make sure to only display a certain number of entries
					if float(n) >= max_n:
						break
					# Set time color to green for your own CP time
					list_time = {'index': n, 'color': "$0f3" if player.login == pcp.player.login else "$bbb"}

					if pcp.player.login in self.app.ko_qualified:
						if (n - 1) < await self.app.get_nr_qualified():
							list_time['virt_qualified'] = True
							list_time['virt_eliminated'] = False
						else:
							list_time['virt_qualified'] = False
							list_time['virt_eliminated'] = True


					# Display 'fin' when the player crossed the finish line else display the CP number
					if pcp.cp == -1 or (pcp.cp == 0 and pcp.time != 0):
						list_time['col0'] = 'fin'
						last_fin += 1
					else:
						list_time['col0'] = str(pcp.cp)
					list_time['col2'] = times.format_time(pcp.time)
					list_time['nickname'] = pcp.player.nickname
					list_time['login'] = pcp.player.login
					# Only show top 5 fins but always show the current player
					if (pcp.cp == -1 or (pcp.cp == 0 and pcp.time != 0)) and last_fin > 5:
						if player.login != pcp.player.login:
							continue
						list_times[4] = list_time
						continue
					list_times.append(list_time)
					n += 1
				scores[player.login] = {'scores': list_times}
			data.update(scores)
			return data



		# In case we are in TA phase
		if self.app.ta_active:
			for player in self.app.instance.player_manager.online:
				list_records = list()

				player_index = len(self.standings_manager.current_rankings) + 1
				if player:
					player_record = [x for x in self.standings_manager.current_rankings if x['login'] == player.login]
				else:
					player_record = list()

				if len(player_record) > 0:
					# Set player index if there is a record
					player_index = (self.standings_manager.current_rankings.index(player_record[0]) + 1)

				records = list(self.standings_manager.current_rankings[:self.top_entries])
				if self.app.instance.performance_mode:
					# Performance mode is turned on, get the top of the whole widget.
					records += self.standings_manager.current_rankings[self.top_entries:self.record_amount]
					custom_start_index = (self.top_entries + 1)
				else:
					if player_index > len(self.standings_manager.current_rankings):
						# No personal record, get the last records
						records_start = (len(self.standings_manager.current_rankings) - self.record_amount + self.top_entries)
						# If start of current slice is in the top entries, add more records below
						if records_start < self.top_entries:
							records_start = self.top_entries

						records += list(self.standings_manager.current_rankings[records_start:])
						custom_start_index = (records_start + 1)
					else:
						if player_index <= self.top_entries:
							# Player record is in top X, get following records (top entries + 1 onwards)
							records += self.standings_manager.current_rankings[self.top_entries:self.record_amount]
							custom_start_index = (self.top_entries + 1)
						else:
							# Player record is not in top X, get records around player record
							# Same amount above the record as below, except when not possible (favors above)
							records_to_fill = (self.record_amount - self.top_entries)
							start_point = ((player_index - math.ceil((records_to_fill - 1) / 2)) - 1)
							end_point = ((player_index + math.floor((records_to_fill - 1) / 2)) - 1)

							# If end of current slice is outside the list, add more records above
							if end_point > len(self.standings_manager.current_rankings):
								end_difference = (end_point - len(self.standings_manager.current_rankings))
								start_point = (start_point - end_difference)
							# If start of current slice is in the top entries, add more records below
							if start_point < self.top_entries:
								start_point = self.top_entries

							records += self.standings_manager.current_rankings[start_point:(start_point + records_to_fill)]
							custom_start_index = (start_point + 1)

				index = 1
				best = None
				for record in records:
					if index == 1:
						best = record
					list_record = dict()
					list_record['col0'] = index
					print(str(index-1) + '<' + str(await self.app.get_nr_qualified()))
					list_record['virt_qualified'] = (index-1) < await self.app.get_nr_qualified()
					list_record['virt_eliminated'] = not list_record['virt_qualified']


					list_record['color'] = '$fff'
					if index <= self.top_entries:
						list_record['color'] = '$ff0'
					if index == player_index:
						list_record['color'] = '$0f3'

					list_record['nickname'] = record['nickname']

					list_record['col2'] = times.format_time(int(record['score']))

					print('index: ' + str(index) + ', nick: ' + str(record['nickname'])
						  + ', time: ' + str(list_record['col2'])
						  + ', qualified: ' + str(list_record['virt_qualified'])
						  + ', eliminated: ' + str(list_record['virt_eliminated']))


					if index == self.top_entries:
						index = custom_start_index
					else:
						index += 1




					list_records.append(list_record)
				data[player.login] = dict(scores=list_records)
			return data

	async def handle_catch_all(self, player, action, values, **kwargs):
		if str(action).startswith('spec_'):
			target = action[5:]
			await self.app.spec_player(player=player, target_login=target)
