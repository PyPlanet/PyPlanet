import aiohttp
import logging
import asyncio

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.ads.view import PayPalLogoView, DiscordLogoView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting
from pyplanet.contrib.command import Command
from pyplanet import __version__ as pyplanet_version


class Ads(AppConfig):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Initiate the logo views.
		self.paypal_view = PayPalLogoView(self, manager=self.context.ui)
		self.discord_view = DiscordLogoView(self, manager=self.context.ui)

		self.paypal_donation_url = None
		self.discord_join_url = None
		self.discord_server_id = None

		# Initiate settings.
		self.setting_enable_paypal = Setting(
			'paypal_enable', 'Show PayPal Donation Logo', Setting.CAT_DESIGN, type=bool,
			description='Show the PayPal logo with clickable link to donation page', change_target=self.reload_settings,
			default=False
		)
		self.setting_paypal_url = Setting(
			'paypal_url', 'PayPal Donation URL', Setting.CAT_KEYS, type=str,
			description='Your personalized PayPal donation link.', change_target=self.reload_settings,
		)

		self.setting_enable_discord = Setting(
			'discord_enable', 'Show Discord Logo', Setting.CAT_DESIGN, type=bool,
			description='Show the Discord logo with clickable link to join the server', change_target=self.reload_settings,
			default=False
		)
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
		# Register signals.
		self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)

		# Register commands.
		await self.instance.command_manager.register(
			Command(command='paypal', target=self.chat_paypal, admin=False)
		)
		await self.instance.command_manager.register(
			Command(command='discord', target=self.chat_discord, admin=False),
		)

		# Register settings.
		await self.context.setting.register(
			self.setting_enable_discord,
			self.setting_enable_paypal,

			self.setting_paypal_url,
			self.setting_discord_join_url,
			self.setting_discord_server_id,
		)

		# Force reload of settings.
		await self.reload_settings()

		# Call the display method.
		await self.display()

	async def display(self, logins=None):
		show_paypal = await self.setting_enable_paypal.get_value()
		show_discord = await self.setting_enable_discord.get_value()

		if show_paypal:
			await self.paypal_view.display(player_logins=logins)
		if show_discord:
			await self.discord_view.display(player_logins=logins)

	async def hide_all(self):
		await asyncio.gather(
			self.paypal_view.hide(),
			self.discord_view.hide(),
		)

	async def on_connect(self, player, *args, **kwargs):
		await self.display(logins=[player.login])

	async def reload_settings(self, *args, **kwargs):
		# Verify PayPal settings and get donation url.
		if await self.setting_enable_paypal.get_value():
			url = await self.setting_paypal_url.get_value()
			if not url:
				await self.instance.chat('$f00$iInvalid PayPal Donation URL, none given!')
			else:
				with aiohttp.ClientSession(headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}) as session:
					try:
						async with session.get(url) as _:
							pass
					except Exception as e:
						await self.instance.chat('$f00$iInvalid PayPal Donation URL')
						logging.error('Error with checking PayPal donation URL.')
						logging.error(e)
				self.paypal_donation_url = url

		# Verify discord settings.
		if await self.setting_enable_discord.get_value():
			url_setting = await self.setting_discord_join_url.get_value(refresh=True)
			id_setting = await self.setting_discord_server_id.get_value(refresh=True)
			url_validity = await self.is_discord_url_valid(url_setting)

			if url_validity:
				self.discord_join_url = url_setting
			else:
				await self.instance.chat('$f00$iInvalid Discord Invite URL')

			id_validity = await self.is_discord_url_valid("https://discordapp.com/api/guilds/" + id_setting + "/widget.json")
			if id_validity:
				self.discord_server_id = id_setting
			else:
				await self.instance.chat('$f00$iInvalid Discord Server ID')

		# Hide & display widgets.
		await self.hide_all()
		await self.display()

	async def chat_paypal(self, player, *args, **kwargs):
		if await self.setting_enable_paypal.get_value():
			message = "$ff0$iYou can donate to us $l[{}]here!".format(self.paypal_donation_url)
			await self.instance.chat(message, player)

	async def chat_discord(self, player, *args, **kwargs):
		if await self.setting_enable_discord.get_value():
			users = await self.get_discord_users()
			if users:
				join_url_link = '$l[' + self.discord_join_url + ']Join our Discord$l! '
				message = '$ff0$i{}There are currently {} users and {} bots online.' \
					.format(join_url_link, users[0], users[1])
				await self.instance.chat(message, player)

	async def get_discord_users(self):
		url = "https://discordapp.com/api/guilds/" + self.discord_server_id + "/widget.json"

		with aiohttp.ClientSession(headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}) as session:
			try:
				async with session.get(url) as response:
					data = await response.json()
					non_bot_users = []
					bots = []
					for i in data['members']:
						if 'bot' in i:
							bots.append(i)
						else:
							non_bot_users.append(i)
					online_users = len(non_bot_users)
					return [int(online_users), int(len(bots))]
			except Exception as e:
				logging.error('Error with retrieving Discord user list')
				logging.error(e)
				return False

	async def is_discord_url_valid(self, url):
		with aiohttp.ClientSession(headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}) as session:
			try:
				async with session.get(url) as _:
					return True
			except Exception as e:
				logging.error('Error with checking for valid Discord URL')
				logging.error(e)
				return False
