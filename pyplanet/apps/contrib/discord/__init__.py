import json
import urllib.request as req
import urllib.error
import logging
from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.discord.view import DiscordLogoView
from pyplanet.contrib.command import Command
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting


class Discord(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.Logo = DiscordLogoView(self, manager=self.context.ui)
		self.join_url = None
		self.server_id = None

		self.setting_discord_join_url = Setting(
			'discord_url', 'Discord Invite URL', Setting.CAT_KEYS, type=str,
			description='Set the link to not expire in discord for this to keep working!',
			default='https://discord.gg/x9amg5K', change_target=self.reload_settings
		)

		self.setting_discord_server_id = Setting(
			'discord_id', 'Discord Server ID', Setting.CAT_KEYS, type=str,
			description='Get your discord server ID and enable the widget in the discord server settings!',
			default='158349559959912448', change_target=self.reload_settings
		)

	async def on_start(self):
		self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)
		await self.instance.command_manager.register(
			Command(command='discord', target=self.chat_msg, admin=False),
		)

		await self.context.setting.register(
			self.setting_discord_join_url, self.setting_discord_server_id
		)
		await self.reload_settings()
		self.Logo = DiscordLogoView(self, manager=self.context.ui)
		await self.Logo.display()

	async def on_connect(self, player, **kwargs):
		await self.Logo.display(player_logins=[player.login])

	async def reload_settings(self, *args, **kwargs):
		url_setting = await self.setting_discord_join_url.get_value(refresh=True)
		id_setting = await self.setting_discord_server_id.get_value(refresh=True)
		url_validity = await self.is_url_valid(url_setting)
		if url_validity:
			self.join_url = url_setting
		else:
			await self.instance.chat('$f00$iInvalid Discord Invite URL')
		id_validity = await self.is_url_valid("https://discordapp.com/api/guilds/" + id_setting + "/widget.json")
		if id_validity:
			self.server_id = id_setting
		else:
			await self.instance.chat('$f00$iInvalid Discord Server ID')
		await self.Logo.display()

	async def is_url_valid(self, url):
		try:
			request = urllib.request.Request(url)
			request.add_header('User-Agent', "PyPlanet")
			logging.debug("URL WAS CHECKED")
			req.urlopen(request).read()
			return True
		except Exception as e:
			logging.error(e)
			return False

	async def get_online_users(self):
		url = "https://discordapp.com/api/guilds/" + self.server_id + "/widget.json"
		request = urllib.request.Request(url)
		request.add_header('User-Agent', "PyPlanet")
		data = json.loads(req.urlopen(request).read())
		non_bot_users = []
		bots = []
		for i in data['members']:
			if 'bot' in i:
				bots.append(i)
			else:
				non_bot_users.append(i)
		online_users = len(non_bot_users)
		return [int(online_users), int(len(bots))]

	async def chat_msg(self, player, *args, **kwargs):
		users = await self.get_online_users()
		join_url_link = '$l[' + self.join_url + ']Join our Discord$l! '
		message = '$ff0$i{}There are currently {} users and {} bots online.' \
			.format(join_url_link, users[0], users[1])
		await self.instance.chat(message, player)
