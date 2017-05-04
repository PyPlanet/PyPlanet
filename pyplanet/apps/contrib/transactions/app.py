from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command


class Transactions(AppConfig):
	name = 'pyplanet.apps.contrib.transactions'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def on_start(self):
		await self.instance.permission_manager.register('pay', 'Pay planets to players', app=self, min_level=3)

		await self.instance.command_manager.register(
			Command(command='pay', target=self.pay_to_player, perms='transactions:pay', admin=True).add_param(name='login', required=True).add_param(name='amount', required=True),
			Command(command='donate', target=self.donate).add_param(name='amount', required=True),
		)

	async def donate(self, player, data, **kwargs):
		try:
			amount = int(data.amount)

			await self.instance.gbx.execute('SendBill', player.login, amount, 'Donating to our lovely server :)')
		except ValueError:
			message = '$z$s$fff» $i$f00The amount should be a numeric value.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def pay_to_player(self, player, data, **kwargs):
		try:
			amount = int(data.amount)

			await self.instance.gbx.execute('Pay', player.login, amount, 'Payment from the server')
		except ValueError:
			message = '$z$s$fff» $i$f00The amount should be a numeric value.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)
