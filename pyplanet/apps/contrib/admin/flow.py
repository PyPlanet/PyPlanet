"""
Game Flow Admin methods and functions.
"""
from pyplanet.contrib.command import Command


class FlowAdmin:
	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.admin.app.Admin
		"""
		self.app = app
		self.instance = app.instance

	async def on_start(self):
		await self.instance.permission_manager.register('end_round', 'Force ending a round (warmup, race or custom)', app=self.app, min_level=2)
		await self.instance.permission_manager.register('points_repartition', 'Change the points repartition', app=self.app, min_level=2)

		# Trackmania specific:
		if self.instance.game.game == 'tm':
			await self.instance.command_manager.register(
				Command(command='endround', target=self.end_round, perms='admin:end_round', admin=True),
				Command(command='endwuround', target=self.end_wu_round, perms='admin:end_round', admin=True),
				Command(command='endwu', target=self.end_wu, perms='admin:end_round', admin=True),
				Command(command='pointsrepartition', aliases=['pointsrep'], target=self.set_point_repartition, perms='admin:points_repartition', admin=True)
					.add_param('repartition', nargs='*', type=str, required=True, help='Repartition, comma or space separated.'),
			)

		# Shootmania specific.
		if self.instance.game.game == 'sm':
			pass

	async def end_round(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.ForceEndRound', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced the current round to end.'.format(player.nickname))
		)

	async def end_wu_round(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.WarmUp.ForceStopRound', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced the current round to end.'.format(player.nickname))
		)

	async def end_wu(self, player, data, **kwargs):
		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.WarmUp.ForceStop', encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has forced the WarmUp to an end.'.format(player.nickname))
		)

	async def set_point_repartition(self, player, data, **kwargs):
		partition = data.repartition

		if len(partition) == 1:
			partition = str(partition[0]).split(',')
		partition = [str(p).strip() for p in partition]

		await self.instance.gbx.multicall(
			self.instance.gbx('Trackmania.SetPointsRepartition', *partition, encode_json=False, response_id=False),
			self.instance.chat('$ff0Admin $fff{}$z$s$ff0 has changed the points repartition to: {}.'.format(
				player.nickname, ','.join(partition))
			)
		)
