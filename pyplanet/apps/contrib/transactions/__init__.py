import asyncio
import logging
import math

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting

from pyplanet.apps.core.maniaplanet import callbacks as mp_signals

from pyplanet.apps.contrib.transactions.view import DonationToolbarWidget

logger = logging.getLogger(__name__)


class Transactions(AppConfig):
	name = 'pyplanet.apps.contrib.transactions'
	game_dependencies = ['trackmania', 'shootmania']
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.current_bills = dict()
		self.min_donation = 10
		self.public_appreciation = 100
		self.lock = asyncio.Lock()

		self.widget = DonationToolbarWidget(self)

		self.setting_display_widget = Setting(
			'donation_widget', 'Display Donation Widget', Setting.CAT_DESIGN, type=bool, default=True,
			description='Display the donation widget to the players',
			change_target=self.reload_settings,
		)
		self.setting_display_widget_podium_only = Setting(
			'donation_widget_podium', 'Display Donation Widget only during podiums', Setting.CAT_BEHAVIOUR, type=bool,
			default=True, description='Enabling this will only display the donation widget on the podium '
									  '(requires the other setting to be enabled as well)',
			change_target=self.reload_settings
		)

	async def on_start(self):
		await self.context.setting.register(
			self.setting_display_widget, self.setting_display_widget_podium_only
		)

		await self.instance.permission_manager.register('pay', 'Pay planets to players', app=self, min_level=3)
		await self.instance.permission_manager.register('planets', 'Display amount of planets', app=self, min_level=3)

		await self.instance.command_manager.register(
			Command(command='planets', target=self.display_planets, perms='transactions:planets', admin=True),
			Command(command='pay', target=self.pay_to_player, perms='transactions:pay', admin=True)
				.add_param(name='login', required=True).add_param(name='amount', required=True),
			Command(command='donate', target=self.donate).add_param(name='amount', required=True),
		)

		# Register callback.
		self.context.signals.listen(mp_signals.other.bill_updated, self.bill_updated)

		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.context.signals.listen(mp_signals.flow.podium_end, self.podium_end)
		self.context.signals.listen(mp_signals.map.map_start, self.map_start)

		# Show widget.
		if await self.setting_display_widget.get_value() and not await self.setting_display_widget_podium_only.get_value():
			await self.widget.display()

	async def reload_settings(self, *args, **kwargs):
		if await self.setting_display_widget.get_value() \
			and not await self.setting_display_widget_podium_only.get_value():
			await self.widget.display()
		elif not await self.setting_display_widget.get_value() \
			or await self.setting_display_widget_podium_only.get_value():
			await self.widget.hide()

	async def player_connect(self, player, *args, **kwargs):
		if not await self.setting_display_widget.get_value():
			return
		if await self.setting_display_widget_podium_only.get_value():
			return

		await self.widget.display(player_logins=[player.login])

	async def podium_start(self, *args, **kwargs):
		if await self.setting_display_widget.get_value() \
			and await self.setting_display_widget_podium_only.get_value():
			await self.widget.display()

	async def podium_end(self, *args, **kwargs):
		if await self.setting_display_widget.get_value() \
			and await self.setting_display_widget_podium_only.get_value():
			await self.widget.hide()

	async def map_start(self, *args, **kwargs):
		if await self.setting_display_widget.get_value() \
			and await self.setting_display_widget_podium_only.get_value():
			await self.widget.hide()

	async def display_planets(self, player, data, **kwargs):
		planets = await self.instance.gbx('GetServerPlanets')
		message = '$ff0Current server balance: $fff{}$ff0 planets.'.format(planets)
		await self.instance.chat(message, player)

	async def donate(self, player, data, **kwargs):
		try:
			async with self.lock:
				amount = abs(int(data.amount))
				if amount >= self.min_donation:
					bill_id = await self.instance.gbx('SendBill', player.login, amount, 'Donating {} planets to our server!'.format(amount), '')
					self.current_bills[bill_id] = dict(bill=bill_id, player=player, amount=amount)
				else:
					message = '$i$f00You need to donate at least $fff{}$f00 planets.'.format(self.min_donation)
					await self.instance.chat(message, player)
		except ValueError:
			message = '$i$f00The amount should be a numeric value.'
			await self.instance.chat(message, player)

	async def pay_to_player(self, player, data, **kwargs):
		try:
			amount = abs(int(data.amount))

			planets = await self.instance.gbx('GetServerPlanets')
			if amount <= (planets - 2 - math.floor(amount * 0.05)):
				async with self.lock:
					bill_id = await self.instance.gbx('Pay', data.login, amount, 'Payment from the server')
					self.current_bills[bill_id] = dict(bill=bill_id, admin=player, player=data.login, amount=-amount)
			else:
				message = '$i$f00Insufficient balance for paying $fff{}$f00 ($fff{}$f00 inc. tax) planets, only got $fff{}$f00.'.format(
					amount, (amount + 2 + math.floor(amount * 0.05)), planets
				)
				await self.instance.chat(message, player)
		except ValueError:
			message = '$z$s$fff» $i$f00The amount should be a numeric value.'
			await self.instance.chat(message, player)

	async def bill_updated(self, bill_id, state, state_name, transaction_id, **kwargs):
		async with self.lock:
			if bill_id not in self.current_bills:
				logger.debug('BillUpdated for unknown BillId {}: "{}" ({}) (TxId {})'.format(bill_id, state_name, state, transaction_id))
				return

			current_bill = self.current_bills[bill_id]
			logger.debug('BillUpdated for BillId {}: "{}" ({}) (TxId {})'.format(bill_id, state_name, state, transaction_id))
			if state == 4:
				if current_bill['amount'] > 0:
					if current_bill['amount'] > self.public_appreciation:
						message = '$f0fWe received a donation of $fff{}$f0f planets from $fff{}$z$s$f0f. Thank You!'.format(current_bill['amount'], current_bill['player'].nickname)
						await self.instance.chat(message)
					else:
						message = '$f0fYou made a donation of $fff{}$f0f planets. Thank You!'.format(current_bill['amount'])
						await self.instance.chat(message, current_bill['player'].login)

					# Update the player's total donations statistics.
					player = current_bill['player']
					player.total_donations += current_bill['amount']
					await player.save()
				else:
					message = '$f0fPayment of $fff{}$f0f planets to $fff{}$f0f confirmed!'.format(-current_bill['amount'], current_bill['player'])
					await self.instance.chat(message, current_bill['admin'].login)

				del self.current_bills[bill_id]
			elif state == 5:
				if current_bill['amount'] > 0:
					message = '$i$f00Transaction refused!'
					await self.instance.chat(message, current_bill['player'].login)
				else:
					message = '$i$f00Transaction refused!'
					await self.instance.chat(message, current_bill['admin'].login)

				del self.current_bills[bill_id]
			elif state == 6:
				if current_bill['amount'] > 0:
					message = '$i$f00Transaction failed: $fff{}$f00!'.format(state_name)
					await self.instance.chat(message, current_bill['player'].login)
				else:
					message = '$i$f00Transaction failed: $fff{}$f00!'.format(state_name)
					await self.instance.chat(message, current_bill['admin'].login)

				del self.current_bills[bill_id]
