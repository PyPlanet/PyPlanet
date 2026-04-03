import asyncio
import logging
import math
from argparse import Namespace
from typing import Optional

from pyplanet.apps.config import AppConfig
from pyplanet.apps.contrib.voting import Voting
from pyplanet.apps.core.maniaplanet.models import Map
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

		self.match_started = False
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
		self.setting_enabled_paid_time_extend = Setting(
			'paid_extension_enabled', 'Paid Time Extend enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not the paid time extend is enabled (only works in TimeAttack mode).'
						' It respects the limit set by `extend_max_amount` setting.'
						' But ignores the `enabled_time_extend` setting (this means that voting can be disabled, but paid extension enabled).',
			default=True,
			change_target=self.reload_settings
		)
		self.setting_paid_extension_base_cost = Setting(
			'paid_extension_base_cost', 'Paid Time Extend Base Cost', Setting.CAT_BEHAVIOUR, type=int,
			description='The base cost in planets to extend the track. This is multiplied by the `paid_extension_cost_multiplier` setting.',
			default=200, change_target=self.reload_settings
		)
		self.setting_paid_extension_cost_multiplier = Setting(
			'paid_extension_cost_multiplier', 'Paid Time Extend Multiplier', Setting.CAT_BEHAVIOUR, type=int,
			description='The multiplier for successive extensions of the same map. This is multiplied by the `paid_extension_base_cost` setting.'
						' For example, if the base cost is 200 planets and the multiplier is 2, then the second extension will cost 400 planets'
						' and the third one 800 planets.',
			default=2, change_target=self.reload_settings
		)
		self.setting_enabled_paid_skip = Setting(
			'paid_skip_enabled', 'Paid Skip enabled', Setting.CAT_BEHAVIOUR, type=bool,
			description='Whether or not the paid skip is enabled.'
						' It ignores the `enabled_skip` setting (this means that voting can be disabled, but paid skip enabled).',
			default=True,
			change_target=self.reload_settings
		)
		self.setting_paid_skip_cost = Setting(
			'paid_skip_cost', 'Paid Skip Cost', Setting.CAT_BEHAVIOUR, type=int,
			description='The cost in planets to skip the track.',
			default=10000, change_target=self.reload_settings
		)

	async def on_start(self):
		await self.context.setting.register(
			self.setting_display_widget, self.setting_display_widget_podium_only, self.setting_enabled_paid_time_extend,
			self.setting_paid_extension_base_cost, self.setting_paid_extension_cost_multiplier,
			self.setting_enabled_paid_skip, self.setting_paid_skip_cost,
		)

		await self.instance.permission_manager.register('pay', 'Pay planets to players', app=self, min_level=3)
		await self.instance.permission_manager.register('planets', 'Display amount of planets', app=self, min_level=3)

		await self.instance.command_manager.register(
			Command(command='planets', target=self.display_planets, perms='transactions:planets', admin=True),
			Command(command='pay', target=self.pay_to_player, perms='transactions:pay', admin=True)
				.add_param(name='login', required=True).add_param(name='amount', required=True),
			Command(command='donate', target=self.donate).add_param(name='amount', required=True),
			Command(command='pay2extend', target=self.pay_to_extend),
			Command(command='pay2skip', target=self.pay_to_skip),
		)

		# Register callback.
		self.context.signals.listen(mp_signals.other.bill_updated, self.bill_updated)

		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.context.signals.listen(mp_signals.flow.podium_start, self.podium_start)
		self.context.signals.listen(mp_signals.flow.podium_end, self.podium_end)

		self.context.signals.listen(mp_signals.flow.round_start, self.match_start)
		self.context.signals.listen(mp_signals.flow.round_end, self.match_end)
		self.context.signals.listen(mp_signals.flow.match_start, self.match_start)
		self.context.signals.listen(mp_signals.flow.match_end, self.match_end)

		self.context.signals.listen(mp_signals.map.map_start, self.map_start)
		# Show widget.
		if await self.setting_display_widget.get_value() and not await self.setting_display_widget_podium_only.get_value():
			await self.widget.display()

	@property
	def voting_app(self) -> Voting:
		return self.instance.apps.apps['voting']

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

	async def match_start(self, *args, **kwargs):
		self.match_started = True

	async def match_end(self, *args, **kwargs):
		self.match_started = False

	async def display_planets(self, player, data, **kwargs):
		planets = await self.instance.gbx('GetServerPlanets')
		message = '$ff0Current server balance: $fff{}$ff0 planets.'.format(planets)
		await self.instance.chat(message, player)

	async def donate(self, player, data, **kwargs):
		try:
			amount = abs(int(data.amount))
			if amount >= self.min_donation:
				async with self.lock:
					bill_id = await self.instance.gbx('SendBill', player.login, amount, 'Donating {} planets to our server!'.format(amount), '')
					self.current_bills[bill_id] = dict(bill=bill_id, player=player, amount=amount)
			else:
				message = '$i$f00You need to donate at least $fff{}$f00 planets.'.format(self.min_donation)
				await self.instance.chat(message, player)
		except ValueError:
			message = '$i$f00The amount should be a numeric value.'
			await self.instance.chat(message, player)

	async def pay_to_extend(self, player, data, **kwargs):
		"""
		Chat command: /pay2extend
		Called when a player wants to extend the map and is willing to pay for it.

		:param player: player initiating the payment
		"""
		logger.debug("Pay to extend called for player {} with data {}".format(player.login, data))

		if 'timeattack' not in (await self.instance.mode_manager.get_current_script()).lower():
			message = '$i$f00Paid Time Extend is only supported in Time Attack modes!'
			await self.instance.chat(message, player)
			return

		if 'voting' not in self.instance.apps.apps:
			message = '$i$f00Voting app needs to be enabled on this server, since it tracks the extension count!'
			await self.instance.chat(message, player)
			return

		extend_max_amount = int(await self.voting_app.setting_extend_max_amount.get_value())

		if 0 < extend_max_amount <= self.voting_app.extend_current_count:
			message = '$i$f00The maximum amount of extensions ({}) has been reached!'.format(extend_max_amount)
			await self.instance.chat(message, player)
			return

		if not self.match_started:
			message = '$i$f00You cannot pay for extension after the match ended! It\'s too late, sorry.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to pay for extension.'
			await self.instance.chat(message, player)
			return

		extension_cost = await self._get_current_extension_cost(player)
		logger.debug("Extension cost: {}".format(extension_cost))
		if extension_cost is None:
			return

		message = '$f0fInitiating payment of $fff{}$f0f planets to extend the track.'.format(extension_cost)
		await self.instance.chat(message, player)

		logger.debug("Sending bill of {} to {}".format(extension_cost, player.login))
		current_map: Map = self.instance.map_manager.current_map
		async with self.lock:
			bill_id = await self.instance.gbx('SendBill', player.login, extension_cost, 'Paying {} planets to our server for extension.'.format(extension_cost), '')
			self.current_bills[bill_id] = dict(bill=bill_id, player=player, amount=extension_cost, map_uid=current_map.uid, extend=True)

	async def pay_to_skip(self, player, data, **kwargs):
		"""
		Chat command: /pay2skip
		Called when a player wants to skip the map and is willing to pay for it.

		:param player: player initiating the payment
		"""
		logger.debug("Pay to skip called for player {} with data {}".format(player.login, data))

		cost = int(await self.setting_paid_skip_cost.get_value())
		if cost <= 0:
			message = '$i$f00Invalid cost set! Please inform admins about that. Current value: $fff{}$f00.'.format(cost)
			await self.instance.chat(message, player)
			return

		if not self.match_started:
			message = '$i$f00You cannot pay to skip after the match ended! Change of the map is already happening.'
			await self.instance.chat(message, player)
			return

		if player.flow.is_spectator:
			message = '$i$f00Only players are allowed to pay to skip.'
			await self.instance.chat(message, player)
			return

		message = '$f0fInitiating payment of $fff{}$f0f planets to skip the track.'.format(cost)
		await self.instance.chat(message, player)

		logger.debug("Sending bill of {} to {}".format(cost, player.login))
		current_map: Map = self.instance.map_manager.current_map
		async with self.lock:
			bill_id = await self.instance.gbx('SendBill', player.login, cost, 'Paying {} planets to our server to skip this track.'.format(cost), '')
			self.current_bills[bill_id] = dict(bill=bill_id, player=player, amount=cost, map_uid=current_map.uid, skip=True)

	async def pay_to_player(self, player, data, **kwargs):
		try:
			logger.debug("Pay to player called for player {} with data {}".format(player.login, data))
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

	async def _get_current_extension_cost(self, player) -> Optional[int]:
		base_cost = int(await self.setting_paid_extension_base_cost.get_value())
		if base_cost <= 0:
			message = '$i$f00Invalid base cost set! Please inform admins about that. Current value: $fff{}$f00.'.format(base_cost)
			await self.instance.chat(message, player)
			return None

		return base_cost * int(await self.setting_paid_extension_cost_multiplier.get_value()) ** self.voting_app.extend_current_count

	async def refund(self, bill_id):
		if bill_id not in self.current_bills:
			logger.debug('Refund for unknown BillId {}'.format(bill_id))
			return

		current_bill = self.current_bills[bill_id]
		logger.debug("Refunding bill ID {}: {}".format(bill_id, current_bill))

		data = Namespace(login=current_bill['player'].login, amount=current_bill['amount'])
		await self.pay_to_player(current_bill['player'], data)

	async def bill_updated(self, bill_id, state, state_name, transaction_id, **kwargs):
		if bill_id not in self.current_bills:
			logger.debug('BillUpdated for unknown BillId {}: "{}" ({}) (TxId {})'.format(bill_id, state_name, state, transaction_id))
			return

		current_bill = self.current_bills[bill_id]
		logger.debug('BillUpdated for BillId {}: "{}" ({}) (TxId {})'.format(bill_id, state_name, state, transaction_id))
		if state == 4:
			if current_bill['amount'] > 0:
				paid_to_skip = 'skip' in current_bill
				paid_to_extend = 'extend' in current_bill

				if paid_to_skip or paid_to_extend:

					operation = 'skip' if paid_to_skip else 'extension'

					# Validate the payment cost first.
					if paid_to_extend:
						# Since extending the map can result in a change of the price, we have to check if it changed in the meantime.
						extension_cost = await self._get_current_extension_cost(current_bill['player'].login)
						if extension_cost is None:
							logger.debug('Extension cost is invalid. Cannot verify the payment. Issuing a refund of {}'.format(current_bill))
							await self.refund(bill_id)

							message = '$i$f00The server-side extension cost became invalid. Refunding you $fff{}$f00 planets.'.format(current_bill['amount'])
							await self.instance.chat(message, current_bill['player'].login)
							return

						if current_bill['amount'] != extension_cost:
							logger.debug('Extension cost changed in the meantime. Issuing a refund of {}'.format(current_bill))
							await self.refund(bill_id)

							message = '$i$f00Somebody has extended the map already, so the actual cost changed already. Refunding you $fff{}$f00 planets.'.format(
								current_bill['amount']
							)
							await self.instance.chat(message, current_bill['player'].login)
							return

					if self.instance.map_manager.current_map.uid != current_bill['map_uid']:
						# Actually, we might have changed the map already in the meantime, which is unfortunate.
						# In this case, we perform a refund.
						logger.debug('Map changed in the meantime. Issuing a refund of {}'.format(current_bill))
						await self.refund(bill_id)

						message = '$i$f00The map has changed in the meantime, so the payment of $fff{}$f00 planets for the {} has been refunded.'.format(
							current_bill['amount'], operation
						)
						await self.instance.chat(message, current_bill['player'].login)
						return
					else:

						voting_app: Voting = self.instance.apps.apps['voting']

						if paid_to_extend:
							if not self.match_started:
								logger.debug('Restarting the map as a result of late payment for extension {}'.format(current_bill))
								await voting_app.vote_restart_passed(None, True)
							else:
								logger.debug('Extending the map as a result of the payment {}'.format(current_bill))
								await voting_app.vote_extend_passed(None, True)
						elif paid_to_skip:
							if not self.match_started:
								logger.debug('Player paid to skip the map, but the map has already ended. Issuing a refund of {}'.format(current_bill))
								await self.refund(bill_id)

								# We might have entered the podium stage before the payment was processed.
								message = '$i$f00The map has already ended. Refunding you $fff{}$f00 planets.'.format(current_bill['amount'])
								await self.instance.chat(message, current_bill['player'].login)
								return

							logger.debug('Skipping the map as a result of the payment {}'.format(current_bill))
							await voting_app.reset_vote()
							await self.instance.gbx('NextMap')

						# Let's publicly appreciate this gesture
						message = '$fff{}$z$s$f0f just paid $fff{}$f0f planets for {}.'.format(
							current_bill['player'].nickname, current_bill['amount'], operation
						)
						await self.instance.chat(message)

				elif current_bill['amount'] > self.public_appreciation:
					message = '$f0fWe received a donation of $fff{}$f0f planets from $fff{}$z$s$f0f. Thank You!'.format(current_bill['amount'], current_bill['player'].nickname)
					await self.instance.chat(message)
				else:
					message = '$f0fYou made a donation of $fff{}$f0f planets. Thank You!'.format(current_bill['amount'])
					await self.instance.chat(message, current_bill['player'].login)

				# Update the player's total donations' statistics.
				player = current_bill['player']
				async with self.lock:
					player.total_donations += current_bill['amount']
					await player.save()
			else:
				message = '$f0fPayment of $fff{}$f0f planets to $fff{}$f0f confirmed!'.format(-current_bill['amount'], current_bill['player'])
				await self.instance.chat(message, current_bill['admin'].login)

			async with self.lock:
				del self.current_bills[bill_id]
		elif state == 5:
			if current_bill['amount'] > 0:
				message = '$i$f00Transaction refused!'
				await self.instance.chat(message, current_bill['player'].login)
			else:
				message = '$i$f00Transaction refused!'
				await self.instance.chat(message, current_bill['admin'].login)

			async with self.lock:
				del self.current_bills[bill_id]
		elif state == 6:
			if current_bill['amount'] > 0:
				message = '$i$f00Transaction failed: $fff{}$f00!'.format(state_name)
				await self.instance.chat(message, current_bill['player'].login)
			else:
				message = '$i$f00Transaction failed: $fff{}$f00!'.format(state_name)
				await self.instance.chat(message, current_bill['admin'].login)

			async with self.lock:
				del self.current_bills[bill_id]
