"""
Player Admin methods and functions.
"""
import asyncio
import logging
import secrets
from random import random

from pyplanet.apps.contrib.admin.views.players import PlayerListView
from pyplanet.conf import settings
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
		self.claim_token = None

	async def on_start(self):
		await self.instance.permission_manager.register('ignore', 'Ignore a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('unignore', 'Unignore a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('kick', 'Kick a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('ban', 'Ban a player', app=self.app, min_level=2)
		await self.instance.permission_manager.register('unban', 'Unban a player', app=self.app, min_level=2)
		await self.instance.permission_manager.register('blacklist', 'Blacklist a player', app=self.app, min_level=3)
		await self.instance.permission_manager.register('unblacklist', 'Unblacklist a player', app=self.app, min_level=3)
		await self.instance.permission_manager.register('manage_admins', 'Manage admin', app=self.app, min_level=3)
		await self.instance.permission_manager.register('list_players', 'List players', app=self.app, min_level=1)
		await self.instance.permission_manager.register('force_spec', 'Force player into spectate', app=self.app, min_level=1)
		await self.instance.permission_manager.register('force_play', 'Force player into player slot', app=self.app, min_level=1)
		await self.instance.permission_manager.register('force_team', 'Force player into a team', app=self.app, min_level=1)
		await self.instance.permission_manager.register('switch_team', 'Force player into the other team', app=self.app, min_level=1)
		await self.instance.permission_manager.register('warn', 'Warn a player', app=self.app, min_level=1)
		await self.instance.permission_manager.register('write_blacklist', 'Write blacklist file', app=self.app, min_level=3)
		await self.instance.permission_manager.register('read_blacklist', 'Read blacklist file', app=self.app, min_level=3)
		await self.instance.permission_manager.register('addguest', 'Guestlist a player', app=self.app, min_level=3)
		await self.instance.permission_manager.register('write_guestlist', 'Read guestlist file', app=self.app, min_level=3)
		await self.instance.permission_manager.register('read_guestlist', 'Read guestlist file', app=self.app, min_level=3)
		await self.instance.permission_manager.register('removeguest', 'Remove a guest', app=self.app, min_level=3)

		await self.instance.command_manager.register(
			Command(command='players', target=self.player_list, perms='admin:list_players', admin=True,
					description='Displays the list of players currently online.'),
			Command(command='mute', aliases=['ignore'], target=self.ignore_player, perms='admin:ignore', admin=True,
					description='Mutes the provided player (sent chat messages will not be visible).').add_param(name='login', required=True),
			Command(command='unmute', aliases=['unignore'], target=self.unignore_player, perms='admin:unignore', admin=True,
					description='Unmutes the provided players (sent chat messages will be visible again).').add_param(name='login', required=True),
			Command(command='kick', target=self.kick_player, perms='admin:kick', admin=True,
					description='Kicks the provided player from the server.').add_param(name='login', required=True),
			Command(command='ban', target=self.ban_player, perms='admin:ban', admin=True,
					description='Bans the provided player from the server (until server restart).').add_param(name='login', required=True),
			Command(command='unban', target=self.unban_player, perms='admin:unban', admin=True,
					description='Unbans the provided player on the server (until server restart).').add_param(name='login', required=True),
			Command(command='blacklist', aliases=['black'], target=self.blacklist_player, perms='admin:blacklist', admin=True,
					description='Blacklists the provided player from the server (permanent ban).').add_param(name='login', required=True),
			Command(command='addguest', aliases=['addguest'], target=self.addguest_player, perms='admin:addguest', admin=True,
					description='Guests the provided player from the server (permanent guest).').add_param(name='login', required=True),
			Command(command='unblacklist', aliases=['unblack'], target=self.unblacklist_player, perms='admin:unblacklist', admin=True,
					description='Unblacklists the provided player on the server.').add_param(name='login', required=True),
			Command(command='removeguest', aliases=['removeguest'], target=self.removeguest_player, perms='admin:removeguest', admin=True,
					description='Remove the provided player on the server as a Guest.').add_param(name='login', required=True),
			Command(command='level', target=self.change_level, perms='admin:manage_admins', description='Changes admin level for the providedplayer.', admin=True)
				.add_param(name='login', required=True)
				.add_param(name='level', required=False, help='Level, 0 = player, 1 = operator, 2 = admin, 3 = master admin.', type=int, default=0),
			Command(command='forcespec', target=self.force_spec, perms='admin:force_spec', description='Forces player into spectator mode.', admin=True)
				.add_param(name='login', required=True),
			Command(command='forceplay', target=self.force_play, perms='admin:force_play', description='Forces player into player slot.', admin=True)
				.add_param(name='login', required=True),
			Command(command='forceteam', target=self.force_team, perms='admin:force_team', description='Forces player into a team.', admin=True)
				.add_param(name='login', required=True, type=str)
				.add_param(name='team', required=True, help='Team, blue/0 = left, red/1 = right'),
			Command(command='switchteam', target=self.switch_team, perms='admin:switch_team', description='Forces player into the other team.', admin=True)
				.add_param(name='login', required=True),
			Command(command='warn', aliases=['warning'], target=self.warn_player, perms='admin:warn', description='Warns the provided player.', admin=True)
				.add_param(name='login', required=True),
			Command(command='writeblacklist', aliases=['wbl'], target=self.write_blacklist, perms='admin:write_blacklist', description='Writes the blacklist file to disk.', admin=True)
				.add_param('file', required=False, type=str, help='Give custom blacklist file to save to.'),
			Command(command='writeguestlist', aliases=['wgl'], target=self.write_guestlist, perms='admin:write_guestlist', description='Writes the guestlist file to disk.', admin=True)
				.add_param('file', required=False, type=str, help='Give custom guest file to save to.'),
			Command(command='readblacklist', aliases=['rbl'], target=self.read_blacklist, perms='admin:read_blacklist', description='Reads the blacklist file from disk.', admin=True)
				.add_param('file', required=False, type=str, help='Give custom blacklist file to load from.'),
			Command(command='readguestlist', aliases=['rgl'], target=self.read_guestlist, perms='admin:read_guestlist', description='Reads the guestlist file from disk.', admin=True)
				.add_param('file', required=False, type=str, help='Give custom guestlist file to load from.'),
			Command(command='claim', target=self.claim_rights, description='Claim admin rights', admin=False)
				.add_param('token', required=True, type=str, help='Token to claim rights.'),
		)

		# Claim timer.
		self.claim_token = secrets.token_hex(8)
		asyncio.ensure_future(self.announce_claim_message())

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

	async def force_play(self, player, data, **kwargs):
		try:
			dest_player = [p for p in self.instance.player_manager.online if p.login == data.login]
			if not len(dest_player) == 1:
				raise Exception()
			message = '$ff0Admin $fff{}$z$s$ff0 has forced $fff{}$z$s$ff0 into player slot.'.format(
				player.nickname, dest_player[0].nickname
			)
			await self.instance.gbx('ForceSpectator', dest_player[0].login, 2)
			await self.instance.gbx.multicall(
				self.instance.gbx('ForceSpectator', dest_player[0].login, 0),
				self.instance.chat(message)
			)
		except Exception as e:
			if 'There are too many players' in str(e):
				message = '$i$f00Too many players!'
			else:
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
			if mute_player.level >= player.level:
				raise PermissionError()
			message = '$ff0Admin $fff{}$z$s$ff0 has muted $fff{}$z$s$ff0.'.format(player.nickname, mute_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('Ignore', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)
		except PermissionError:
			message = '$i$f00Can\'t perform this action on an admin at the same or higher level as you!'
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
			if kick_player.level >= player.level:
				raise PermissionError()

			message = '$ff0Admin $fff{}$z$s$ff0 has kicked $fff{}$z$s$ff0.'.format(player.nickname, kick_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('Kick', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)
		except PermissionError:
			message = '$i$f00Can\'t perform this action on an admin at the same or higher level as you!'
			await self.instance.chat(message, player)

	async def ban_player(self, player, data, **kwargs):
		try:
			ban_player = await self.instance.player_manager.get_player(data.login)
			if ban_player.level >= player.level:
				raise PermissionError()
			message = '$ff0Admin $fff{}$z$s$ff0 has banned $fff{}$z$s$ff0.'.format(player.nickname, ban_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('Ban', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)
		except PermissionError:
			message = '$i$f00Can\'t perform this action on an admin at the same or higher level as you!'
			await self.instance.chat(message, player)

	async def unban_player(self, player, data, **kwargs):
		message = '$ff0Admin $fff{}$z$s$ff0 has un-banned $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx('UnBan', data.login),
			self.instance.chat(message)
		)

	async def addguest_player(self, player, data, **kwargs):
		try:
			guest_player = await self.instance.player_manager.get_player(data.login)
			if guest_player.level >= player.level:
				raise PermissionError()
			message = '$ff0Admin $fff{}$z$s$ff0 has added to the Guestlist: $fff{}$z$s$ff0.'.format(player.nickname, guest_player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('AddGuest', data.login),
				self.instance.chat(message)
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player)
		except PermissionError:
			message = '$i$f00Can\'t perform this action on an admin at the same or higher level as you!'
			await self.instance.chat(message, player)

	async def removeguest_player(self, player, data, **kwargs):
		message = '$ff0Admin $fff{}$z$s$ff0 has removed from the Guestlist: $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx('RemoveGuest', data.login),
			self.instance.chat(message)
		)

	async def blacklist_player(self, player, data, **kwargs):
		try:
			blacklist_player = await self.instance.player_manager.get_player(data.login)
			if blacklist_player.level >= player.level:
				raise PermissionError()

			message = '$ff0Admin $fff{}$z$s$ff0 has blacklisted $fff{}$z$s$ff0.'.format(player.nickname, blacklist_player.nickname)


			try:
				await self.instance.gbx.multicall(
					self.instance.gbx('BlackList', data.login),
					self.instance.gbx('Kick', data.login),
				)
			except:
				return await self.instance.chat('$ff0Blacklisting failed!', player)

			await self.instance.chat(message)

			# Try to save to file.
			try:
				await self.instance.player_manager.save_blacklist()
			except:
				pass
		except PlayerNotFound:
			message = '$ff0Admin $fff{}$z$s$ff0 has blacklisted $fff{}$z$s$ff0.'.format(player.nickname, data.login)
			await self.instance.gbx.multicall(
				self.instance.gbx('BlackList', data.login),
				self.instance.chat(message)
			)
		except PermissionError:
			message = '$i$f00Can\'t perform this action on an admin at the same or higher level as you!'
			await self.instance.chat(message, player)

	async def unblacklist_player(self, player, data, **kwargs):
		message = '$ff0Admin $fff{}$z$s$ff0 has un-blacklisted $fff{}$z$s$ff0.'.format(player.nickname, data.login)
		await self.instance.gbx.multicall(
			self.instance.gbx('UnBlackList', data.login),
			self.instance.chat(message)
		)

		# Try to save to file.
		try:
			await self.instance.player_manager.save_blacklist()
		except:
			pass

	async def write_guestlist(self, player, data, **kwargs):
		setting = settings.GUESTLIST_FILE
		if isinstance(setting, dict) and self.instance.process_name in setting:
			setting = setting[self.instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not setting and not data.file:
			message = '$ff0Default guestlist file setting not configured in your settings file!'
			await self.instance.chat(message, player)
			return

		if data.file:
			file_name = data.file
		else:
			file_name = setting.format(server_login=self.instance.game.server_player_login)

		message = '$ff0Guestlist has been saved to the file: {}'.format(file_name)
		try:
			await self.instance.player_manager.save_guestlist(filename=file_name)
			await self.instance.chat(message, player)
		except:
			await self.instance.chat('$ff0Guestlist saving failed to {}'.format(file_name), player)

	async def read_guestlist(self, player, data, **kwargs):
		setting = settings.GUESTLIST_FILE
		if isinstance(setting, dict) and self.instance.process_name in setting:
			setting = setting[self.instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not setting and not data.file:
			message = '$ff0Default Guest list file setting not configured in your settings file!'
			await self.instance.chat(message, player)
			return

		if data.file:
			file_name = data.file
		else:
			file_name = setting.format(server_login=self.instance.game.server_player_login)

		message = '$ff0Guestlist has been loaded from the file: {}'.format(file_name)
		try:
			await self.instance.player_manager.load_guestlist(filename=file_name)
			await self.instance.chat(message, player)
		except:
			await self.instance.chat('$ff0Guestlist loading failed from {}'.format(file_name), player)


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
				self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has warned $fff{}$z$s$ff0.'.format(player.nickname, warn_player.nickname))
			)
		except PlayerNotFound:
			message = '$i$f00Unknown login!'
			await self.instance.chat(message, player.login)
			return

	async def write_blacklist(self, player, data, **kwargs):
		setting = settings.BLACKLIST_FILE
		if isinstance(setting, dict) and self.instance.process_name in setting:
			setting = setting[self.instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not setting and not data.file:
			message = '$ff0Default blacklist file setting not configured in your settings file!'
			await self.instance.chat(message, player)
			return

		if data.file:
			file_name = data.file
		else:
			file_name = setting.format(server_login=self.instance.game.server_player_login)

		message = '$ff0Blacklist has been saved to the file: {}'.format(file_name)
		try:
			await self.instance.player_manager.save_blacklist(filename=file_name)
			await self.instance.chat(message, player)
		except:
			await self.instance.chat('$ff0Blacklist saving failed to {}'.format(file_name), player)

	async def read_blacklist(self, player, data, **kwargs):
		setting = settings.BLACKLIST_FILE
		if isinstance(setting, dict) and self.instance.process_name in setting:
			setting = setting[self.instance.process_name]
		if not isinstance(setting, str):
			setting = None

		if not setting and not data.file:
			message = '$ff0Default blacklist file setting not configured in your settings file!'
			await self.instance.chat(message, player)
			return

		if data.file:
			file_name = data.file
		else:
			file_name = setting.format(server_login=self.instance.game.server_player_login)

		message = '$ff0Blacklist has been loaded from the file: {}'.format(file_name)
		try:
			await self.instance.player_manager.load_blacklist(filename=file_name)
			await self.instance.chat(message, player)
		except:
			await self.instance.chat('$ff0Blacklist loading failed from {}'.format(file_name), player)

	async def player_list(self, player, data, **kwargs):
		view = PlayerListView(self.app, player)
		await view.display()

	async def claim_rights(self, player, data, **kwargs):
		if data.token != self.claim_token:
			await self.instance.chat('$ff0Claiming rights failed. Failure has been logged!', player)
			logging.getLogger(__name__).error('Security: User {} ({}) tried to claim rights'.format(player.nickname, player.login))
			return

		player.level = 3
		await player.save()
		await self.instance.chat('$fff{}$z$s$ff0 has claimed admin rights.'.format(player.nickname))

	async def announce_claim_message(self):
		await asyncio.sleep(4)
		logging.getLogger(__name__).info(
			'Welcome to PyPlanet, to claim admin rights, copy and paste this in the chat: /claim {}'.format(self.claim_token)
		)
