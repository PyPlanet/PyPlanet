import random

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.funcmd.view import EmojiToolbarView
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting

from pyplanet.utils.style import style_strip


class FunCmd(AppConfig):
	app_dependencies = ['core.maniaplanet']

	muffins = [
		'Muffin',
		'Apple Cinnamon Muffin',
		'Cornbread Muffin',
		'Blueberry Cream Cheese Muffin',
		'Sweet Potato Muffin',
		'Chocolate Muffin',
		'Coffee Cake Muffin',
		'Snickerdoodle Mini Muffin',
		'Oatmeal Muffin',
		'Cinnamon Streusel Muffin',
		'Apple Cider Muffin',
		'Toffe-ee Muffin ;-)',
		'Insert-Developer-Joke-Here Muffin',
		'Orange Marmalade Muffin',
		'Pumpkin Spice Muffin',
		'Cranberry Oatmeal Muffin',
		'Pineapple & Sour Cream Muffin',
		'Lemon Yogurt Muffin',
		'Zucchini Muffin',
		'Slice of Apple Pie',
		'Baklava',
		'Bowl of Gelato',
		'Picarones',
		'Syrniki',
		'Lamingtons',
		'Cup of Skyr',
		'Om Ali',
		'Bread Pudding',
		'Loukoumades',
		'Slice of Spekkoek',
		'Slice of Slagroomtaart',
		'Appelflappen',
		'Banana Muffin',
		'No Muffin',
		'Blueberry Muffin',
		'Two Muffins',
		'Muffin with Cream',
		'Choc-Chip Muffin',
		'Double Chocolate Muffin',
		'Lemmon & Poppyseed Muffin',
		'Apple Crunch Muffin',
		'Raspberry Muffin',
		'Pink Cupcake',
		'Pumpkin Pie',
		'Slice of Cheesecake',
		'Cinnamon Doghnut',
		'Carrot Cake',
	]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setting_emoji_toolbar = Setting(
			'emoji_toolbar', 'Display Emoji Toolbar', Setting.CAT_DESIGN, type=bool, default=True,
			description='Display the Emoji Toolbar to users.',
			change_target=self.reload_settings
		)

		self.emoji_toolbar = EmojiToolbarView(self)

	async def on_start(self):
		await self.context.setting.register(
			self.setting_emoji_toolbar
		)

		await self.instance.command_manager.register(
			Command(command='afk', target=self.command_afk, admin=False, description='Set yourself as AFK'),
			Command(command='bootme', target=self.command_bootme, admin=False, description='Boot yourself from the server'),
			Command(command='rq', aliases=['ragequit'], target=self.command_rq, admin=False, description='Ragequit from the server'),
			Command(command='gg', target=self.command_gg, admin=False, description='Send Good Game to everyone'),
			Command(command='n1', target=self.command_n1, admin=False, description='Send Nice One to everyone'),
			Command(command='nt', target=self.command_nt, admin=False, description='Send Nice Try/Nice Time to everyone'),
			Command(command='muffin', target=self.command_muffin, admin=False, description='Give muffin to another player').add_param(name='login', required=True),
		)

		if self.instance.game.game == 'sm':
			await self.instance.command_manager.register(
				Command(command='ns', target=self.command_ns, admin=False, description='Send Nice Shot to everyone'),
			)

		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)

		if await self.setting_emoji_toolbar.get_value():
			await self.emoji_toolbar.display()

	async def reload_settings(self, *args, **kwargs):
		if await self.setting_emoji_toolbar.get_value():
			await self.emoji_toolbar.display()
		else:
			await self.emoji_toolbar.hide()

	async def player_connect(self, player, *args, **kwargs):
		if await self.setting_emoji_toolbar.get_value():
			await self.emoji_toolbar.display(player_logins=[player.login])

	async def command_afk(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		await self.instance.gbx.multicall(
			self.instance.gbx('ForceSpectator', player.login, 3),
			self.instance.chat('$fff {}$z$s$fff is now away from keyboard.'.format(player.nickname))
		)

	async def command_muffin(self, player, data, **kwargs):
		# Try to match the player.
		if self.instance.game.game == 'tmnext':
			nickname_input = style_strip(data.login).lower()
			dest_player = [p for p in self.instance.player_manager.online if style_strip(p.nickname.lower()) == nickname_input]
		else:
			dest_player = [p for p in self.instance.player_manager.online if p.login == data.login]

		# Try to get the nickname of the destination player, otherwise just show the input login.
		if dest_player:
			dest_nickname = dest_player[0].nickname
		else:
			dest_nickname = data.login

		# Prepare the message.
		muffin = random.choice(self.muffins)
		a_word = 'a'
		if muffin[0:1].lower() in ['a', 'e', 'u', 'i', 'o']:
			a_word = 'an'

		message = '$z$s{}$z$s$m$f90 gave {} {} to $z$s{}'.format(
			player.nickname, a_word, muffin, dest_nickname
		)

		# Send the message.
		await self.instance.chat(message)

	async def command_bootme(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		await self.instance.gbx.multicall(
			self.instance.chat('$fff  {}$z$s$fff chooses to boot back to real life!'.format(player.nickname)),
			self.instance.gbx('Kick', player.login, 'chooses to boot to real life (/bootme)'),
		)

	async def command_rq(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		await self.instance.gbx.multicall(
			self.instance.chat('$f00 {}$z$s$f00 rage quits.'.format(player.nickname)),
			self.instance.gbx('Kick', player.login, 'rage quit (/rq)'),
		)

	async def command_gg(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		await self.instance.chat('$fff {}$z$s$fff Good Game everyone!'.format(player.nickname))

	async def command_n1(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		await self.instance.chat('$fff {}$z$s$fff Nice one!'.format(player.nickname))

	async def command_ns(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		await self.instance.chat('$fff {}$z$s$fff Nice shot!'.format(player.nickname))

	async def command_nt(self, player, data, **kwargs):
		if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
			return
		if self.instance.game.game == 'sm':
			await self.instance.chat('$fff {}$z$s$fff Nice try!'.format(player.nickname))
		else:
			await self.instance.chat('$fff {}$z$s$fff Nice time!'.format(player.nickname))
