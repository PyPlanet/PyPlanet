"""
Game Flow Admin methods and functions.
"""
from pyplanet.contrib.command import Command


class FlowAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('end_round', 'Force ending a round (warmup, race or custom)', app=self.app, min_level=2)
		await self.instance.permission_manager.register('pause', 'Force Pause (warmup, race or custom)', app=self.app, min_level=2)
		await self.instance.permission_manager.register('player_points', 'Change the player points', app=self.app, min_level=2)
		await self.instance.permission_manager.register('team_points', 'Change the team points', app=self.app, min_level=2)
		await self.instance.permission_manager.register('points_repartition', 'Change the points repartition', app=self.app, min_level=2)

		# Trackmania specific:
		if self.instance.game.game == 'tm' or self.instance.game.game == 'tmnext':
			await self.instance.command_manager.register(
				Command(command='endround', target=self.end_round, perms='admin:end_round', admin=True,
						description='Ends the current round of play.'),
				Command(command='pause', target=self.pause, perms='admin:pause', admin=True,
						description='Pauses a Match.'),
				Command(command='unpause', target=self.unpause, perms='admin:pause', admin=True,
						description='Continues a Match.'),
				Command(command='endwuround', target=self.end_wu_round, perms='admin:end_round', admin=True,
						description='Ends the current warm-up round of play.'),
				Command(command='endwu', target=self.end_wu, perms='admin:end_round', admin=True,
						description='Ends the complete warm-up on this map.'),
				Command(command='pointsrepartition', aliases=['pointsrep'], target=self.set_point_repartition,
						perms='admin:points_repartition', admin=True, description='Alters the points repartitioning.')
					.add_param('repartition', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
				Command(command='playerpoints', aliases=['playerpoints'], target=self.set_player_points,
						perms='admin:player_points', admin=True, description='Alters the Players Points for Round, Map, Match.')
						.add_param(name='login', required=True)
						.add_param(name='points', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
				Command(command='teampoints', aliases=['teampoints'], target=self.set_team_points,
						perms='admin:team_points', admin=True, description='Alters the Teams Points for Round, Map, Match.')
						.add_param(name='teamid', required=True)
						.add_param(name='points', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
				Command(command='pd', target=self.set_pd_name,
						perms='admin:points_repartition', admin=True, description='Alters the points repartitioning.')
					.add_param('name', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
				)

		# Shootmania specific.
		if self.instance.game.game == 'sm':
			await self.instance.command_manager.register(
				Command(command='playerpoints', aliases=['playerpoints'], target=self.set_player_points,
						perms='admin:player_points', admin=True, description='Alters the Players Points for Round, Map, Match.')
						.add_param(name='login', required=True)
						.add_param(name='points', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
				Command(command='teampoints', aliases=['teampoints'], target=self.set_team_points,
						perms='admin:team_points', admin=True, description='Alters the Teams Points for Round, Map, Match.')
						.add_param(name='teamid', required=True)
						.add_param(name='points', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
				)

	async def end_round(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.ForceEndRound', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced the current round to end.'.format(player.nickname))
		)
	
	async def pause(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Maniaplanet.Pause.SetActive', 'true', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced a Pause of the Match.'.format(player.nickname))
		)
		
	async def unpause(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Maniaplanet.Pause.SetActive', 'false', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced to continue the Match.'.format(player.nickname))
		)	
	async def end_wu_round(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.WarmUp.ForceStopRound', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced the current round to end.'.format(player.nickname))
		)

	async def end_wu(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.WarmUp.ForceStop', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced the WarmUp to an end.'.format(player.nickname))
		)
	
	async def set_pd_name(self, player, data, **kwargs):
		pd = data.name
		
		if 'smurfs' in pd:
			points_smurfs = str('50,45,41,38,36,34,32,30,28,26,24,22,20,18,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,1,1').split(',')
			#print(points_smurfs)
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_smurfs)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_smurfs]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, '$06fSmurfs Cup'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'f1old' in pd:
			points_f1old = str('10,8,6,5,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_smurfs)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_f1old]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'F1 Old'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'f1new' in pd:
			points_f1new = str('25,18,15,12,10,8,6,4,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_f1new)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_f1new]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'F1 New'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'motogp' in pd:
			points_motogp = str('25,20,16,13,11,10,9,8,7,6,5,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_motogp)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_motogp]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'MotoGP'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'motogp5' in pd:
			points_motogp5 = str('30,25,21,18,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_motogp5)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_motogp5]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'MotoGP + 5'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'fet1' in pd:
			points_fet1 = str('12,10,9,8,7,6,5,4,4,3,3,3,2,2,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_fet1)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_fet1]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Formula ET Season 1'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
			
		if 'fet2' in pd:
			points_fet2 = str('15,12,11,10,9,8,7,6,6,5,5,4,4,3,3,3,2,2,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_fet2)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_fet2]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Formula ET Season 2'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'fet3' in pd:
			points_fet3 = str('15,12,11,10,9,8,7,6,6,5,5,4,4,3,3,3,2,2,2,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_fet3)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_fet3]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Formula ET Season 3'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'champcar' in pd:
			points_champcar = str('31,27,25,23,21,19,17,15,13,11,10,9,8,7,6,5,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_champcar)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_champcar]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Champ Car World Series'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'superstars' in pd:
			points_superstars = str('20,15,12,10,8,6,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_superstars)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_superstars]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Superstars'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'simple5' in pd:
			points_simple5 = str('5,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_simple5)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_simple5]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Simple 5'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
		if 'simple10' in pd:
			points_simple10 = str('10,9,8,7,6,5,4,3,2,1').split(',')
			remove_content = ["'", "[", "]"] # Content you want to be removed from `str`
			my_str = repr(points_simple10)  # convert list to `str`
			for content in remove_content:
				my_str = my_str.replace(content, '')
			
			partition = [str(p).strip() for p in points_simple10]
			await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, 'Simple 10'))
			)
			await self.instance.mode_manager.update_settings({'S_PointsRepartition': str(my_str)})
		
	async def set_point_repartition(self, player, data, **kwargs):
		partition = data.repartition

		if len(partition) == 1:
			partition = str(partition[0]).split(',')
		partition = [str(p).strip() for p in partition]

		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, ','.join(partition))
			)
		)
		
	async def set_player_points(self, player, data, **kwargs):
		login = data.login
		points = data.points
		if len(points) == 1:
			points = str(points[0]).split(',')
		points = [str(p).strip() for p in points]
		
		#login, 'RoundPoints', 'Mappoints', 'Matchpoints' for Sending/Updating PlayerPoints
		if self.instance.game.game == 'sm':
			method_playerpoints = 'Shootmania.SetPlayerPoints'
		if self.instance.game.game in ['tm', 'tmnext']:
			method_playerpoints = 'Trackmania.SetPlayerPoints'
		await self.instance.gbx.multicall(
				self.instance.gbx(method_playerpoints, login, *points, encode_json=False, response_id=False),
				self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points distribution for Player: $fff{} $z$s$ff0 to: {}'.format(
				player.nickname, login, points)
			))
			
	async def set_team_points(self, player, data, **kwargs):
		teamid = data.teamid
		points = data.points
		if len(points) == 1:
			points = str(points[0]).split(',')
		points = [str(p).strip() for p in points]
		
		#TeamId, 'RoundPoints', 'Mappoints', 'Matchpoints' for Sending/Updating TeamPoints
		#TeamId = 0 (Blue) or 1 (Red)
		if self.instance.game.game == 'sm':
			method_teampoints = 'Shootmania.SetTeamPoints'
		if self.instance.game.game in ['tm', 'tmnext']:
			method_teampoints = 'Trackmania.SetTeamPoints'
		await self.instance.gbx.multicall(
				self.instance.gbx(method_teampoints, teamid, *points, encode_json=False, response_id=False),
				self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points distribution for Team: $fff{} $z$s$ff0 to: {}'.format(
				player.nickname, teamid, points)
			))
