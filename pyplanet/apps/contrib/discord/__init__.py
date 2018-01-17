import json
import urllib.request as req
import urllib
from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.discord.view import DiscordLogoView
from pyplanet.contrib.command import Command
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class Discord(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	join_url = 'https://discord.gg/teQ8Bsy'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.Logo = DiscordLogoView(manager=self.context.ui)

	async def on_start(self):
		self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)
		await self.instance.command_manager.register(
			Command(command='discord', target=self.chat_msg, admin=False),
		)
		self.Logo = DiscordLogoView(manager=self.context.ui)
		await self.Logo.display()

	async def on_connect(self, player, **kwargs):
		await self.Logo.display(player_logins=[player.login])

	async def get_online_users(self):
		url = "https://discordapp.com/api/guilds/403261055498977291/widget.json"
		request = urllib.request.Request(url)
		request.add_header('User-Agent', "PyPlanet")
		data = json.loads(req.urlopen(request).read())
		online_users = len(data['members'])
		return int(online_users)

	async def chat_msg(self, *args, **kwargs):
		number_of_online_users = await self.get_online_users()
		join_url_link = '$l[{self.join_url}]Join our Discord$l! '
		message = '$ff0$i{}There are currently {} users online.'\
			.format(join_url_link, number_of_online_users)
		await self.instance.chat(message)
