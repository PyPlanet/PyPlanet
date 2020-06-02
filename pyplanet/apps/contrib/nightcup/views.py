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
			'type': 'label'
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
					await self.parent.app.instance.chat(message, player)
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
	size_y = 113
	title = 'NightCup'

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

		# This determines the amount of records that will fit in the widget
		max_n = min(math.floor((self.size_y - 5.5) / 3.3), self.record_amount)

		scores = {}

		if self.app.ta_active:
			# Handling with TA data
			round_data = self.standings_manager.current_rankings
		elif self.app.ko_active:
			# Handling with KO data
			round_data = self.standings_manager.player_cps
		else:
			# In any other case there is no data
			return data

		for player in self.app.instance.player_manager.online:
			focused_index = len(round_data) + 1
			focused = player
			if player:
				spectator_status = (await self.app.instance.gbx('GetPlayerInfo', player.login))['SpectatorStatus']
				target_id = spectator_status // 10000
				if target_id:
					# Player is spectating someone
					target = await self.app.instance.player_manager.get_player_by_id(target_id)
					focused = target or player
			if focused:
				if self.app.ta_active:
					player_record = [x for x in round_data if x['login'] == focused.login]
				elif self.app.ko_active:
					player_record = [x for x in round_data if x.player.login == focused.login]
				else:
					return data
				if player_record:
					focused_index = round_data.index(player_record[0]) + 1

			records = list(round_data[:self.top_entries])
			if self.app.instance.performance_mode:
				records += round_data[self.top_entries:max_n]
				custom_start_index = self.top_entries + 1
			else:
				if focused_index >= len(round_data):
					# No personal record, get the last records
					records_start = max(len(round_data) - max_n + self.top_entries, self.top_entries)

					# If start of current slice is in the top entries, add more records below
					records += list(round_data[records_start:])
					custom_start_index = records_start + 1
				else:
					if focused_index <= self.top_entries:
						# Player record is in top X, get following records (top entries + 1 onwards)
						records += round_data[self.top_entries:max_n]
						custom_start_index = self.top_entries + 1
					else:
						# Player record is not in top X, get records around player record
						# Same amount above the record as below, except when not possible (favors above)
						records_to_fill = max_n - self.top_entries
						start_point = focused_index - math.ceil((records_to_fill - 1) / 2) - 1
						end_point = focused_index + math.floor((records_to_fill - 1) / 2) - 1

						# If end of current slice is outside the list, add more records above
						if end_point > len(round_data):
							end_difference = end_point - len(round_data)
							# If start of current slice is in the top entries, add more records below
							start_point = (start_point - end_difference)
						# If start of current slice is in the top entries, add more records below
						if start_point < self.top_entries:
							start_point = self.top_entries
						records += round_data[start_point:start_point + records_to_fill]
						custom_start_index = start_point + 1

			list_records = list()
			index = 1
			for record in records:
				list_record = dict()
				if index == focused_index:
					list_record['color'] = '$0ff'
				elif index <= self.top_entries:
					list_record['color'] = '$ff0'
				else:
					list_record['color'] = '$fff'

				if self.app.ta_active:
					list_record['virt_qualified'] = index - 1 < await self.app.get_nr_qualified()
					list_record['virt_eliminated'] = not list_record['virt_qualified']
					list_record['col0'] = index
					list_record['login'] = record['login']
					list_record['nickname'] = record['nickname']
					list_record['time'] = times.format_time(int(record['score']))
				elif self.app.ko_active:
					if record.player.login in self.app.ko_qualified:
						virt_qualified = [rec.player.login for rec in records if rec.player.login in self.app.ko_qualified]
						list_record['virt_qualified'] = (virt_qualified.index(record.player.login)) < await self.app.get_nr_qualified()
						list_record['virt_eliminated'] = not list_record['virt_qualified']
					else:
						list_record['virt_qualified'] = False
						list_record['virt_eliminated'] = False
					list_record['col0'] = 'fin' if record.cp == -1 else str(record.cp)
					list_record['login'] = record.player.login
					list_record['nickname'] = record.player.nickname
					list_record['time'] = times.format_time(record.time)


				index = custom_start_index if index == self.top_entries else index + 1

				list_records.append(list_record)
			data[player.login] = dict(scores=list_records)
		return data

	async def handle_catch_all(self, player, action, values, **kwargs):
		if str(action).startswith('spec_'):
			target = action[5:]
			await self.app.spec_player(player=player, target_login=target)

