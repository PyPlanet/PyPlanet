"""
Player Admin methods and functions.
"""
import asyncio

from pyplanet.contrib.command import Command
from pyplanet.contrib.player.exceptions import PlayerNotFound
from pyplanet.views.generics.alert import show_alert


class PlayerAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('ignore', 'Ignore a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('unignore', 'Unignore a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('kick', 'Kick a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('ban', 'Ban a player', app=self.app, min_level=2)
		await self.instance.permission_manager.register('unban', 'Unban a player', app=self.app, min_level=2)
		await self.instance.permission_manager.register('blacklist', 'Blacklist a player', app=self.app, min_level=3)
		await self.instance.permission_manager.register('unblacklist', 'Unblacklist a player', app=self.app, min_level=3)
		await self.instance.permission_manager.register('manage_admins', 'Manage admin', app=self.app, min_level=3)
		await self.instance.permission_manager.register('force_spec', 'Force player into spectate', app=self.app, min_level=1)
		await self.instance.permission_manager.register('force_team', 'Force player into a team', app=self.app, min_level=1)
		await self.instance.permission_manager.register('switch_team', 'Force player into the other team', app=self.app, min_level=1)
		await self.instance.permission_manager.register('warn', 'Warn a player', app=self.app, min_level=1)

		await self.instance.command_manager.register(
			Command(command='mute', aliases=['ignore'], target=self.ignore_player, perms='admin:ignore', admin=True).add_param(name='login', required=True),
			Command(command='unmute', aliases=['unignore'], target=self.unignore_player, perms='admin:unignore', admin=True).add_param(name='login', required=True),
			Command(command='kick', target=self.kick_player, perms='admin:kick', admin=True).add_param(name='login', required=True),
			Command(command='ban', target=self.ban_player, perms='admin:ban', admin=True).add_param(name='login', required=True),
			Command(command='unban', target=self.unban_player, perms='admin:unban', admin=True).add_param(name='login', required=True),
			Command(command='blacklist', aliases=['black'], target=self.blacklist_player, perms='admin:blacklist', admin=True).add_param(name='login', required=True),
			Command(command='unblacklist', aliases=['unblack'], target=self.unblacklist_player, perms='admin:unblacklist', admin=True).add_param(name='login', required=True),
			Command(command='level', target=self.change_level, perms='admin:manage_admins', description='Change admin level for player.', admin=True)
				.add_param(name='login', required=True)
				.add_param(name='level', required=False, help='Level, 0 = player, 1 = operator, 2 = admin, 3 = master admin.', type=int, default=0),
			Command(command='forcespec', target=self.force_spec, perms='admin:force_spec', description='Force player into spectate', admin=True)
				.add_param(name='login', required=True),
			Command(command='forceteam', target=self.force_team, perms='admin:force_team', description='Force player into a team', admin=True)
				.add_param(name='login', required=True, type=str)
				.add_param(name='team', required=True, help='Team, blue/0 = left, red/1 = right'),
			Command(command='switchteam', target=self.switch_team, perms='admin:switch_team', description='Force player into the other team', admin=True)
				.add_param(name='login', required=True),
			Command(command='warn', aliases=['warning'], target=self.warn_player, perms='admin:warn', description='Warn a player', admin=True)
				.add_param(name='login', required=True)
		)

	async def force_spec(self, player, data, **kwargs):
		try:
			dest_player = [p for p in self.instance.player_manager.online if p.login == data.login]
			if not len(dest_player) == 1:
				raise Exception()
			message = '$ff0Admin $fff{}$z$s$ff0 has forced $fff{}$z$s$ff0 into spectator.'.format(
				player.nickname, dest_player[0].nickname
			)
			await self.instance.gbx.multicall(
				self.instance.gbx('ForceSpectator', dest_player[0].login, 3),
				self.instance.chat(message)
			)
		except Exception:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)

	async def force_team(self, player, data, **kwargs):
		dest_player = [p for p in self.instance.player_manager.online if p.login == data.login]
		if not len(dest_player) == 1:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)
			return

		new_team = None
		team_name = ''
		if data.team == 'blue' or data.team == '0':
			new_team = 0
			team_name = '$00fBLUE'
		elif data.team == 'red' or data.team == '1':
			new_team = 1
			team_name = '$f00RED'

		if new_team is None:
			message = '$i$f00Unknown team identifier ($fff{}$z$s$f00)!'.format(data.team)
			await self.instance.chat(message, player)
			return

		message = '$ff0Admin $fff{}$z$s$ff0 has forced $fff{}$z$s$ff0 into team $fff{}$ff0.'.format(
			player.nickname, dest_player[0].nickname, team_name
		)
		await self.instance.gbx.multicall(
			self.instance.gbx('ForcePlayerTeam', dest_player[0].login, new_team),
			self.instance.chat(message)
		)

	async def switch_team(self, player, data, **kwargs):
		dest_player = [p for p in self.instance.player_manager.online if p.login == data.login]
		if not len(dest_player) == 1:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)
			return

		new_team = None
		team_name = ''
		if dest_player[0].flow.team_id == 1:
			new_team = 0
			team_name = '$00fBLUE'
		elif dest_player[0].flow.team_id == 0:
			new_team = 1
			team_name = '$f00RED'

		if new_team is None:
			message = '$i$f00Unable to switch team (are you in a team mode?)!'
			await self.instance.chat(message, player)
			return

		message = '$ff0Admin $fff{}$z$s$ff0 has forced $fff{}$z$s$ff0 into team $fff{}$ff0.'.format(
			player.nickname, dest_player[0].nickname, team_name
		)
		await self.instance.gbx.multicall(
			self.instance.gbx('ForcePlayerTeam', dest_player[0].login, new_team),
			self.instance.chat(message)
		)

	async def ignore_player(self, player, data, **kwargs):
		try:
			if data.login not in self.instance.player_manager.online_logins:
				raise PlayerNotFound()

			mute_player = await self.instance.player_manager.get_player(data.login)
			message = '$ff0Admin $fff{}$z$s$ff0 has muted $fff{}$z$s$ff0.'.format(player.nickname, mute_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('Ignore', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)

	async def unignore_player(self, player, data, **kwargs):
		try:
			if data.login not in self.instance.player_manager.online_logins:
				raise PlayerNotFound()

			unmute_player = await self.instance.player_manager.get_player(data.login)
			message = '$ff0Admin $fff{}$z$s$ff0 has un-muted $fff{}$z$s$ff0.'.format(player.nickname, unmute_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('UnIgnore', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)

	async def kick_player(self, player, data, **kwargs):
		try:
			if data.login not in self.instance.player_manager.online_logins:
				raise PlayerNotFound()

			kick_player = await self.instance.player_manager.get_player(data.login)
			message = '$ff0Admin $fff{}$z$s$ff0 has kicked $fff{}$z$s$ff0.'.format(player.nickname, kick_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('Kick', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)

	async def ban_player(self, player, data, **kwargs):
		try:
			ban_player = await self.instance.player_manager.get_player(data.login)
			message = '$ff0Admin $fff{}$z$s$ff0 has banned $fff{}$z$s$ff0.'.format(player.nickname, ban_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('Ban', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)

	async def unban_player(self, player, data, **kwargs):
		message = '$ff0Admin $fff{}$z$s$ff0 has un-banned $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx('UnBan', data.login),
			self.instance.chat(message)
		)

	async def blacklist_player(self, player, data, **kwargs):
		try:
			blacklist_player = await self.instance.player_manager.get_player(data.login)
			message = '$ff0Admin $fff{}$z$s$ff0 has blacklisted $fff{}$z$s$ff0.'.format(player.nickname, blacklist_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('BlackList', data.login),
				self.instance.gbx('Kick', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$ff0Admin $fff{}$z$s$ff0 has blacklisted $fff{}$z$s$ff0.'.format(player.nickname, data.login)
			await self.instance.gbx.multicall(
				self.instance.gbx('BlackList', data.login),
				self.instance.chat(message)
			)

	async def unblacklist_player(self, player, data, **kwargs):
		message = '$ff0Admin $fff{}$z$s$ff0 has un-blacklisted $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx('UnBlackList', data.login),
			self.instance.chat(message)
		)

	async def change_level(self, player, data, **kwargs):
		try:
			target_player = await self.instance.player_manager.get_player(login=data.login)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player.login)
			return

		if data.level < 0 or data.level > 3:
			message = '$i$f00Level must be between 0 and 3! 0=player, 1=operator, 2=admin, 3=masteradmin.'
			await self.instance.chat(message, player)
			return

		old_level_name = target_player.get_level_string()
		target_player.level = data.level
		new_level_name = target_player.get_level_string()
		await target_player.save()

		if data.level > 0:
			message = '$ff0Admin $fff{}$z$s$ff0 has added $fff{}$z$s$ff0 as an {}.'.format(
				player.nickname, target_player.nickname, new_level_name
			)
		else:
			message = '$ff0Admin $fff{}$z$s$ff0 has removed $fff{}$z$s$ff0 as an {}.'.format(
				player.nickname, target_player.nickname, old_level_name
			)
		await self.instance.chat(message)

	async def warn_player(self, player, data, **kwargs):
		try:
			warn_player = await self.instance.player_manager.get_player(login=data.login, lock=False)

			await asyncio.gather(
				show_alert(
					warn_player,
					'You have just been warned! Ask the present admin for further information and / or potential consequences.',
					size='sm', buttons=None
				),
				self.instance.chat('$i$ff0 Player {} $z$s$i$ff0has received a warning'.format(warn_player.nickname), player)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player.login)
			return
