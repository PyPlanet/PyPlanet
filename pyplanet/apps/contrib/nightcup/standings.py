import math

from pyplanet.utils import times
from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class StandingsLogicManager:

	def __init__(self, app):
		self.app = app

		self.current_cps = {}
		self.standings_widget = None
		self.player_cps = []

	def start(self):
		self.app.context.signals.listen(tm_signals.waypoint, self.player_cp)
		self.app.context.signals.listen(tm_signals.start_line, self.player_start)
		self.app.context.signals.listen(tm_signals.finish, self.player_finish)
		self.app.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.app.context.signals.listen(mp_signals.player.player_disconnect, self.player_disconnect)
		self.app.context.signals.listen(mp_signals.map.map_start__end, self.map_end)
		self.app.context.signals.listen(mp_signals.player.player_enter_spectator_slot, self.player_enter_spec)

		# Make sure we move the rounds_scores and other gui elements.
		self.app.instance.ui_manager.properties.set_attribute('round_scores', 'pos', '-126.5 87. 150.')
		self.app.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')

		self.standings_widget = NcStandingsWidget(self.app)
		self.standings_widget.display()

	def set_standings_widget_title(self, title):
		self.standings_widget.title = title

	# When a player passes a CP
	async def player_cp(self, player, race_time, raw, *args, **kwargs):
		cp = int(raw['checkpointinrace'])  # Have to use raw to get the current CP
		# Create new PlayerCP object if there is no PlayerCP object for that player yet
		if player.login not in self.current_cps:
			self.current_cps[player.login] = PlayerCP(player)
		self.current_cps[player.login].cp = cp + 1  # +1 because checkpointinrace starts at 0
		self.current_cps[player.login].time = race_time
		await self.update_standings_widget()

	# When a player starts the race
	async def player_start(self, player, *args, **kwargs):
		if player.login not in self.current_cps:
			self.current_cps[player.login] = PlayerCP(player)
		await self.update_standings_widget()

	# When a player passes the finish line
	async def player_finish(self, player, race_time, race_cps, is_end_race, raw, *args, **kwargs):
		# Create new PlayerCP object if there is no PlayerCP object for that player yet
		if player.login not in self.current_cps:
			self.current_cps[player.login] = PlayerCP(player)

		# Set the current CP to -1 (signals finished) when a player finishes the race
		if is_end_race:
			self.current_cps[player.login].cp = -1
		else:
			self.current_cps[player.login].cp = int(
				raw['checkpointinrace']) + 1  # Otherwise just update the current cp
		# logging.debug(raw)
		self.current_cps[player.login].time = race_time
		await self.update_standings_widget()

	# When a player connects
	async def player_connect(self, player, *args, **kwargs):
		await self.update_standings_widget()

	# When a player disconnects
	async def player_disconnect(self, player, *args, **kwargs):
		# Remove the current CP from the widget when a player leaves the server
		self.current_cps.pop(player.login, None)
		await self.update_standings_widget()

	# When a player enters spectator mode
	async def player_enter_spec(self, player, *args, **kwargs):
		# Remove the current CP from the widget when a player starts to spectate
		self.current_cps.pop(player.login, None)
		await self.update_standings_widget()

	# When the map ends
	async def map_end(self, *args, **kwargs):
		self.current_cps.clear()  # Clear the current CPs when the map ends
		await self.update_standings_widget()

	# Update the view for all players
	async def update_standings_widget(self):
		# Used for sorting the PlayerCP objects by the 1. CP and 2. the time (Finished players are always on top)
		def keyfunc(key):
			lpcp = self.current_cps[key]
			return 1 if lpcp.cp == -1 else 2, -lpcp.cp, lpcp.time

		self.player_cps.clear()

		# Sort the PlayerCP objects by using the key function above and copy them into the player_cps-list
		for login in sorted(self.current_cps, key=lambda x: keyfunc(x)):
			pcp = self.current_cps[login]
			cp = pcp.cp
			cpstr = str(cp)
			if cp == -1:
				cpstr = "fin"
			self.player_cps.append(pcp)
		await self.standings_widget.display()  # Update the widget for all players

	async def spec_player(self, player, target_login):
		await self.app.instance.gbx.multicall(
			self.app.instance.gbx('ForceSpectator', player.login, 3),
			self.app.instance.gbx('ForceSpectatorTarget', player.login, target_login, -1)
		)

class PlayerCP:
	def __init__(self, player, cp=0, time=0):
		self.player = player
		self.cp = cp
		self.time = time
		self.virt_qualified = False
		self.virt_eliminated = False


class NcStandingsWidget(TimesWidgetView):
	widget_x = -160
	widget_y = 70.5
	top_entries = 5
	z_index = 30
	size_x = 38
	size_y = 55.5
	title = 'Current CPs'

	template_name = 'nightcup/ncstandings.xml'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_nightcupstandings'

		self.record_amount = 30

	async def get_all_player_data(self, logins):
		data = await super().get_all_player_data(logins)

		max_n = math.floor((self.size_y - 5.5) / 3.3)

		# In case no nightcup is active or there is a break
		if not self.app.nc_active:
			cps = {}

			for idx, player in enumerate(self.app.instance.player_manager.online):
				last_fin = 0
				list_times = []
				n = 1
				for pcp in self.app.player_cps:
					# Make sure to only display a certain number of entries
					if float(n) >= max_n:
						break

					# Set time color to green for your own CP time
					list_time = {'index': n, 'color': "$0f3" if player.login == pcp.player.login else "$bbb"}

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
				cps[player.login] = {'cps': list_times}

			data.update(cps)

			return data

		# In case we are in TA phase
		if self.app.ta_active:
			cps = {}
			for idx, player in enumerate(self.app.instance.player_manager.online):
				last_fin = 0
				list_times = []
				n = 1
				for pcp in self.app.player_cps:
					# Make sure to only display a certain number of entries
					if float(n) >= max_n:
						break

					# Set time color to green for your own CP time
					list_time = {'col0': n, 'color': "$0f3" if player.login == pcp.player.login else "$bbb"}

					if pcp.player.login in self.app.ko_qualified:
						if (n - 1) < len(self.app.ko_qualified) - await self.app.get_nr_kos(len(self.app.ko_qualified)):
							list_time['virt_qualified'] = True
							list_time['virt_eliminated'] = False
						else:
							list_time['virt_qualified'] = False
							list_time['virt_eliminated'] = True

					list_time['nr_qualified'] = len(self.app.ko_qualified) - await self.app.get_nr_kos(
						len(self.app.ko_qualified))

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
				cps[player.login] = {'cps': list_times}
			data.update(cps)
			return data


		# In case we are in KO phase
		if self.app.ko_active:
			cps = {}
			for idx, player in enumerate(self.app.instance.player_manager.online):
				last_fin = 0
				list_times = []
				n = 1
				for pcp in self.app.player_cps:
					# Make sure to only display a certain number of entries
					if float(n) >= max_n:
						break

					# Set time color to green for your own CP time
					list_time = {'index': n, 'color': "$0f3" if player.login == pcp.player.login else "$bbb"}

					if pcp.player.login in self.app.ko_qualified:
						if (n-1) < len(self.app.ko_qualified) - await self.app.get_nr_kos(len(self.app.ko_qualified)):
							list_time['virt_qualified'] = True
							list_time['virt_eliminated'] = False
						else:
							list_time['virt_qualified'] = False
							list_time['virt_eliminated'] = True

					list_time['nr_qualified'] = len(self.app.ko_qualified) - await self.app.get_nr_kos(len(self.app.ko_qualified))

					# Display 'fin' when the player crossed the finish line else display the CP number
					if pcp.cp == -1 or (pcp.cp == 0 and pcp.time != 0):
						list_time['cp'] = 'fin'
						last_fin += 1
					else:
						list_time['cp'] = str(pcp.cp)

					list_time['cptime'] = times.format_time(pcp.time)
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
				cps[player.login] = {'cps': list_times}
			data.update(cps)
			return data

	async def handle_catch_all(self, player, action, values, **kwargs):
		if str(action).startswith('spec_'):
			target = action[5:]
			await self.app.spec_player(player=player, target_login=target)
