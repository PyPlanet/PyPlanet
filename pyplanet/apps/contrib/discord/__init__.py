import json
import urllib.request as req
import urllib
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
		self.Logo = DiscordLogoView(manager=self.context.ui)
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
		self.Logo = DiscordLogoView(manager=self.context.ui)
		await self.Logo.display()

	async def on_connect(self, player, **kwargs):
		await self.Logo.display(player_logins=[player.login])

	async def reload_settings(self, *args, **kwargs):
		self.join_url = await self.setting_discord_join_url.get_value(refresh=True)
		self.server_id = await self.setting_discord_server_id.get_value(refresh=True)

	async def get_online_users(self):
		url = "https://discordapp.com/api/guilds/" + self.server_id + "/widget.json"
		request = urllib.request.Request(url)
		request.add_header('User-Agent', "PyPlanet")
		logging.debug(url)
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
