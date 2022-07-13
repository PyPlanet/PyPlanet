import logging

from pyplanet.apps.config import AppConfig
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from .view import CPWidgetView


class CurrentCPs(AppConfig):
	game_dependencies = ['trackmania', 'trackmania_next']
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_cps = {}  # Maps a player login to a PlayerCP object
		self.widget = None
		self.player_cps = []  # Holds the sorted PlayerCP objects (these get displayed by the widget)

		self.dedimania_enabled = False

	# FOR TESTING ONLY, DO NOT USE IN PRODUCTION CODE
	def fill_test_cps(self):
		"""
			Adds some virtual players to the current cps
		"""
		self.current_cps['test1'] = PlayerCP(VirtualPlayer('$b$wTesT1', 'test1'), 4, 74213)
		self.current_cps['test2'] = PlayerCP(VirtualPlayer('$b$wTesT2', 'test2'), -1, 50214)
		self.current_cps['test3'] = PlayerCP(VirtualPlayer('$b$wTesT3', 'test3'), 2, 74215)
		self.current_cps['test4'] = PlayerCP(VirtualPlayer('$b$wTesT4', 'test4'), -1, 62216)
		self.current_cps['test5'] = PlayerCP(VirtualPlayer('$b$wTesT5', 'test5'), 6, 74217)
		self.current_cps['test6'] = PlayerCP(VirtualPlayer('$b$wTesT6', 'test6'), -1, 54218)
		self.current_cps['test7'] = PlayerCP(VirtualPlayer('$b$wTesT7', 'test7'), 1, 74219)
		self.current_cps['test8'] = PlayerCP(VirtualPlayer('$b$wTesT8', 'test8'), 2, 74220)
		self.current_cps['test9'] = PlayerCP(VirtualPlayer('$b$wTesT9', 'test9'), 3, 74221)
		self.current_cps['test10'] = PlayerCP(VirtualPlayer('$b$wTesT10', 'test10'), 6, 74222)
		self.current_cps['test11'] = PlayerCP(VirtualPlayer('$b$wTesT11', 'test11'), 5, 74223)
		self.current_cps['test12'] = PlayerCP(VirtualPlayer('$b$wTesT12', 'test12'), -1, 60225)
		self.current_cps['test13'] = PlayerCP(VirtualPlayer('$b$wTesT13', 'test13'), -1, 64226)
		self.current_cps['test14'] = PlayerCP(VirtualPlayer('$b$wTesT14', 'test14'), 5, 74227)
		self.current_cps['test15'] = PlayerCP(VirtualPlayer('$b$wTesT15', 'test15'), -1, 70228)
		self.current_cps['test16'] = PlayerCP(VirtualPlayer('$b$wTesT16', 'test16'), 3, 74229)
		self.current_cps['test17'] = PlayerCP(VirtualPlayer('$b$wTesT17', 'test17'), -1, 54230)
		self.current_cps['test18'] = PlayerCP(VirtualPlayer('$b$wTesT18', 'test18'), 3, 74231)
		self.current_cps['test19'] = PlayerCP(VirtualPlayer('$b$wTesT19', 'test19'), 4, 74232)
		self.current_cps['test20'] = PlayerCP(VirtualPlayer('$b$wTesT20', 'test20'), 5, 74233)

	async def on_start(self):
		# Listen to some signals
		self.context.signals.listen(tm_signals.waypoint, self.player_cp)
		self.context.signals.listen(tm_signals.start_line, self.player_start)
		self.context.signals.listen(tm_signals.finish, self.player_finish)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.player.player_disconnect, self.player_disconnect)
		self.context.signals.listen(mp_signals.map.map_start__end, self.map_start)
		self.context.signals.listen(mp_signals.player.player_enter_spectator_slot, self.player_enter_spec)

		# Make sure we move the rounds_scores and other gui elements.
		if self.instance.game.game in ['tm', 'sm']:
			self.instance.ui_manager.properties.set_attribute('round_scores', 'pos', '-126.5 80. 150.')
			self.instance.ui_manager.properties.set_attribute('multilap_info', 'pos', '107., 88., 5.')

		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)

		self.widget = CPWidgetView(self)
		# await self.widget.display()
		await self.update_view()

	# When a player passes a CP
	async def player_cp(self, player, race_time, raw, *args, **kwargs):
		cp = int(raw['checkpointinrace'])  # Have to use raw to get the current CP
		# Create new PlayerCP object if there is no PlayerCP object for that player yet
		if player.login not in self.current_cps:
			self.current_cps[player.login] = PlayerCP(player)
		self.current_cps[player.login].cp = cp + 1  # +1 because checkpointinrace starts at 0
		self.current_cps[player.login].time = race_time
		await self.update_view()

	# When a player starts the race
	async def player_start(self, player, *args, **kwargs):
		if player.login not in self.current_cps:
			self.current_cps[player.login] = PlayerCP(player)
		await self.update_view()

	# When a player passes the finish line
	async def player_finish(self, player, race_time, race_cps, is_end_race, raw, *args, **kwargs):
		# Create new PlayerCP object if there is no PlayerCP object for that player yet
		if player.login not in self.current_cps:
			self.current_cps[player.login] = PlayerCP(player)

		# Set the current CP to -1 (signals finished) when a player finishes the race
		if is_end_race:
			self.current_cps[player.login].cp = -1
		else:
			self.current_cps[player.login].cp = int(raw['checkpointinrace']) + 1  # Otherwise just update the current cp
			# logging.debug(raw)
		self.current_cps[player.login].time = race_time
		await self.update_view()

	# When a player connects
	async def player_connect(self, player, *args, **kwargs):
		await self.update_view()
		logging.debug("Player connected: " + player.login)

	# When a player disconnects
	async def player_disconnect(self, player, *args, **kwargs):
		# Remove the current CP from the widget when a player leaves the server
		self.current_cps.pop(player.login, None)
		await self.update_view()

	# When a player enters spectator mode
	async def player_enter_spec(self, player, *args, **kwargs):
		# Remove the current CP from the widget when a player starts to spectate
		self.current_cps.pop(player.login, None)
		await self.update_view()

	# When the map start (end of event)
	async def map_start(self, *args, **kwargs):
		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)
		self.current_cps.clear()  # Clear the current CPs when the map ends
		await self.update_view()

	# Update the view for all players
	async def update_view(self):
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

		await self.widget.display()  # Update the widget for all players

	async def spec_player(self, player, target_login):
		logging.debug(player.login + ' will now spec ' + target_login)
		logging.debug(await self.instance.gbx.multicall(
			self.instance.gbx('ForceSpectator', player.login, 3),
			self.instance.gbx('ForceSpectatorTarget', player.login, target_login, -1)
		))


class PlayerCP:
	def __init__(self, player, cp=0, time=0):
		self.player = player
		self.cp = cp
		self.time = time


class VirtualPlayer:
	def __init__(self, nickname, login):
		self.nickname = nickname
		self.login = login
