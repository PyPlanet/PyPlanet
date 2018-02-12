import aiohttp
import logging

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.paypal.view import PayPalLogoView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.setting import Setting
from pyplanet.contrib.command import Command
from pyplanet import __version__ as pyplanet_version


class PayPal(AppConfig):
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.Logo = PayPalLogoView(self, manager=self.context.ui)
		self.donation_url = None

		self.setting_paypal_url = Setting(
			'paypal_url', 'PayPal Donation URL', Setting.CAT_KEYS, type= str,
			description='Your personalized PayPal donation link.', change_target=self.reload_settings
		)

	async def on_start(self):
		self.context.signals.listen(mp_signals.player.player_connect, self.on_connect)
		await self.instance.command_manager.register(
			Command(command='paypal', target=self.chat_msg, admin=False)
		)
		await self.context.setting.register(
			self.setting_paypal_url
		)
		await self.reload_settings()
		self.Logo = PayPalLogoView(self, manager=self.context.ui)
		await self.Logo.display()

	async def on_connect(self, player, *args, **kwargs):
		await self.Logo.display(player_logins=[player.login])

	async def reload_settings(self, *args, **kwargs):
		url = await self.setting_paypal_url.get_value(refresh=True)
		with aiohttp.ClientSession(headers={'User-Agent': 'PyPlanet/{}'.format(pyplanet_version)}) as session:
			try:
				await session.get(url)
			except Exception as e:
				await self.instance.chat('$f00$iInvalid PayPal Donation URL')
				logging.error(e)
				return
		self.donation_url = url

	async def chat_msg(self, player, *args, **kwargs):
		message = "$ff0$iYou can donate to us $l[{}]here!".format(self.donation_url)
		await self.instance.chat(message, player)
