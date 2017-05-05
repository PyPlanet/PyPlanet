from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals


class Transactions(AppConfig):
	name = 'pyplanet.apps.contrib.transactions'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_bills = []

	async def on_start(self):
		await self.instance.permission_manager.register('pay', 'Pay planets to players', app=self, min_level=3)
		await self.instance.permission_manager.register('planets', 'Display amount of planets', app=self, min_level=3)

		await self.instance.command_manager.register(
			Command(command='planets', target=self.display_planets, perms='transactions:planets', admin=True),
			Command(command='pay', target=self.pay_to_player, perms='transactions:pay', admin=True).add_param(name='login', required=True).add_param(name='amount', required=True),
			Command(command='donate', target=self.donate).add_param(name='amount', required=True),
		)

		# Register callback.
		self.instance.signal_manager.listen(mp_signals.other.bill_updated, self.bill_updated)

	async def display_planets(self, player, data, **kwargs):
		planets = await self.instance.gbx.execute('GetServerPlanets')
		message = '$z$s$fff» $ff0Current server balance: $fff{}$ff0 planets.'.format(planets)
		await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def donate(self, player, data, **kwargs):
		try:
			amount = int(data.amount)
			billid = await self.instance.gbx.execute('SendBill', player.login, amount, 'Donating {} planets to our server!'.format(amount), '')
			self.current_bills.append(dict(bill=billid, player=player, amount=amount))
		except ValueError:
			message = '$z$s$fff» $i$f00The amount should be a numeric value.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def pay_to_player(self, player, data, **kwargs):
		try:
			amount = int(data.amount)
			billid = await self.instance.gbx.execute('Pay', player.login, amount, 'Payment from the server')
			self.current_bills.append(dict(bill=billid, player=player, amount=-amount))
		except ValueError:
			message = '$z$s$fff» $i$f00The amount should be a numeric value.'
			await self.instance.gbx.execute('ChatSendServerMessageToLogin', message, player.login)

	async def bill_updated(self, bill_id, state, state_name, transaction_id, **kwargs):
		if bill_id in self.current_bills:
			print('BillUpdated for BillId {} {} (TxId {})'.format(bill_id, state_name, transaction_id))
		else:
			print('BillUpdated for unknown BillId {} {} (TxId {})'.format(bill_id, state_name, transaction_id))
			print(self.current_bills)
