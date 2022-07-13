"""
Server Admin methods and functions.
"""
import asyncio

from pyplanet.apps.core.maniaplanet.callbacks.player import player_chat
from pyplanet.contrib.command import Command
from xmlrpc.client import Fault

from pyplanet.apps.contrib.admin.views.setting import ModeSettingMenuView


class ServerAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

		self.chat_redirection = False

	async def on_start(self):
		await self.instance.permission_manager.register('callvoting', 'Handle server callvoting', app=self.app, min_level=1)
		await self.instance.permission_manager.register('password', 'Set the server passwords', app=self.app, min_level=2)
		await self.instance.permission_manager.register('servername', 'Set the server name', app=self.app, min_level=2)
		await self.instance.permission_manager.register('mode', 'Set the server game mode', app=self.app, min_level=2)
		await self.instance.permission_manager.register('chat_toggle', 'Turn the public chat on or off', app=self.app, min_level=2)

		await self.instance.command_manager.register(
			Command(command='cancelcallvote', aliases=['cancelcall'], target=self.cancel_callvote, perms='admin:callvoting',
					admin=True, description='Cancels the current callvote (server vote).'),
			Command(command='setpassword', aliases=['srvpass'], target=self.set_password, perms='admin:password', admin=True,
					description='Sets the player password of the server.').add_param(name='password', required=False),
			Command(command='setspecpassword', aliases=['spectpass'], target=self.set_spec_password, perms='admin:password',
					admin=True, description='Sets the spectator password of the server.').add_param(name='password', required=False),
			Command(command='servername', target=self.set_servername, perms='admin:servername', admin=True,
					description='Changes the name of the server.').add_param(name='server_name', required=True, nargs='*'),
			Command(command='mode', target=self.set_mode, perms='admin:mode', admin=True,
					description='Changes the gamemode of the server.').add_param(name='mode', required=True, nargs='*'),
			Command(command='modesettings', target=self.mode_settings, perms='admin:mode', admin=True,
					description='Displays and allows for updating of the gamemode settings.')
				.add_param(name='setting', required=False)
				.add_param(name='content', required=False),
			Command(command='chat', target=self.chat_toggle, perms='admin:chat_toggle', admin=True,
					description='Enables/disables the chat.')
				.add_param(name='enable', required=False),
		)

		# Register signal receivers.
		player_chat.register(self.on_chat)

	async def cancel_callvote(self, player, data, **kwargs):
		current_callvote = await self.instance.gbx('GetCurrentCallVote')

		if current_callvote['CmdName'] == '':
			message = '$i$f00There is currently no callvote active.'
			await self.instance.chat(message, player)
		else:
			message = '$ff0Admin $fff{}$z$s$ff0 has cancelled the current call vote.'.format(player.nickname)
			await self.instance.gbx.multicall(
				self.instance.gbx('CancelVote'),
				self.instance.chat(message)
			)

	async def chat_toggle(self, player, data, **kwargs):
		if data.enable:
			self.chat_redirection = bool(data.enable.lower() == 'on')
		else:
			self.chat_redirection = bool(not self.chat_redirection)
		await self.instance.gbx('ChatEnableManualRouting', self.chat_redirection, True)
		await self.instance.chat('$ff0Admin $fff{}$z$s$ff0 {} public chat'.format(
			player.nickname, 'disabled' if self.chat_redirection else 'enabled'
		))

	async def on_chat(self, player, text, cmd, **kwargs):
		if not cmd and self.chat_redirection:
			if player.level > 0:
				asyncio.ensure_future(self.instance.chat(
					'$z[{}$z$s] {}'.format(player.nickname, text), raw=True
				))

	async def set_mode(self, player, data, **kwargs):
		mode = (' '.join(data.mode))
		lower_mode = mode.lower()
		if self.instance.game.game == 'tm':
		
			if lower_mode == 'ta' or lower_mode == 'timeattack':
				mode = 'TimeAttack.Script.txt'
			elif lower_mode == 'laps':
				mode = 'Laps.Script.txt'
			elif lower_mode == 'rounds':
				mode = 'Rounds.Script.txt'
			elif lower_mode == 'cup':
				mode = 'Cup.Script.txt'
			elif lower_mode == 'chase':
				mode = 'Chase.Script.txt'
			elif lower_mode == 'team':
				mode = 'Team.Script.txt'
			
		if self.instance.game.game == 'tmnext':
		
			if lower_mode == 'ta' or lower_mode == 'timeattack':
				mode = 'Trackmania/TM_TimeAttack_Online.Script.txt'
			elif lower_mode == 'laps':
				mode = 'Trackmania/TM_Laps_Online.Script.txt'
			elif lower_mode == 'rounds':
				mode = 'Trackmania/TM_Rounds_Online.Script.txt'
			elif lower_mode == 'cup':
				mode = 'Trackmania/TM_Cup_Online.Script.txt'
			elif lower_mode == 'team':
				mode = 'Trackmania/TM_Teams_Online.Script.txt'
			elif lower_mode == 'knockout':
				mode = 'Trackmania/TM_Knockout_Online.Script.txt'
			elif lower_mode == 'champion':
				mode = 'Trackmania/TM_Champion_Online.Script.txt'

		try:
			await self.instance.mode_manager.set_next_script(mode)
		except Exception as e:
			message = '$ff0Mode change failed: {}'.format(str(e))
			await self.instance.chat(message, player)
			return
		message = '$ff0Admin $fff{}$z$s$ff0 has changed the next mode to {}'.format(
			player.nickname, mode
		)
		await self.instance.chat(message)

	async def mode_settings(self, player, data, **kwargs):
		setting_name = data.setting
		if setting_name is None:
			view = ModeSettingMenuView(self.app, player)
			await view.display(player=player.login)
		else:
			if not data.content:
				message = '$i$f00Setting a mode setting requires $fff2$f00 parameters.'
				await self.instance.chat(message, player)
				return

			current_settings = await self.instance.mode_manager.get_settings()
			setting_value = data.content
			if setting_name not in current_settings:
				message = '$i$f00Unknown mode setting "$fff{}$f00".'.format(setting_name)
				await self.instance.chat(message, player)
				return

			current_value = current_settings[setting_name]
			current_type = type(current_value)

			type_setting = None
			try:
				if isinstance(current_value, bool):
					lower_setting_value = setting_value.lower()
					if lower_setting_value == 'true' or setting_value == '1':
						type_setting = True
					elif lower_setting_value == 'false' or setting_value == '0':
						type_setting = False
					else:
						raise ValueError
				else:
					type_setting = current_type(setting_value)

				type_setting = current_type(setting_value)
				await self.instance.mode_manager.update_settings({
					setting_name: type_setting
				})

				message = '$ff0Changed mode setting "$fff{}$ff0" to "$fff{}$ff0" (was: "$fff{}$ff0").'.format(setting_name, type_setting, current_value)
				await self.instance.chat(message, player)
			except ValueError:
				message = '$i$f00Unable to cast "$fff{}$f00" to required type ($fff{}$f00) for "$fff{}$f00".'.format(setting_value, current_type, setting_name)
				await self.instance.chat(message, player)
			except Fault as exception:
				message = '$i$f00Unable to set "$fff{}$f00" to "$fff{}$f00": $fff{}$f00.'.format(setting_name, type_setting, exception)
				await self.instance.chat(message, player)

	async def set_servername(self, player, data, **kwargs):
		name = ' '.join(data.server_name)
		message = '$ff0Admin $fff{}$z$s$ff0 has changed the server name into {}'.format(player.nickname, name)
		await self.instance.gbx.multicall(
			self.instance.gbx('SetServerName', name),
			self.instance.chat(message)
		)

	async def set_spec_password(self, player, data, **kwargs):
		if data.password is None or data.password == 'none':
			message = '$ff0You removed the spectator password.'
			await self.instance.gbx.multicall(
				self.instance.gbx('SetServerPasswordForSpectator', ''),
				self.instance.chat(message, player)
			)
		else:
			message = '$ff0You changed the spectator password to: "$fff{}$ff0".'.format(data.password)
			await self.instance.gbx.multicall(
				self.instance.gbx('SetServerPasswordForSpectator', data.password),
				self.instance.chat(message, player)
			)

		await self.app.context.signals.get_signal('maniaplanet:server_password').send(
			dict(password=data.password, kind='spectator'), True
		)

	async def set_password(self, player, data, **kwargs):
		if data.password is None or data.password == 'none':
			message = '$ff0You removed the server password.'
			await self.instance.gbx.multicall(
				self.instance.gbx('SetServerPassword', ''),
				self.instance.chat(message, player)
			)
		else:
			message = '$ff0You changed the server password to: "$fff{}$ff0".'.format(data.password)
			await self.instance.gbx.multicall(
				self.instance.gbx('SetServerPassword', data.password),
				self.instance.chat(message, player)
			)

		await self.app.context.signals.get_signal('maniaplanet:server_password').send(
			dict(password=data.password, kind='player'), True
		)
