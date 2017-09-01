import datetime

from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.contrib.local_records.models import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Player, Map
from pyplanet.apps.core.statistics.models import Score
from pyplanet.contrib.converter.base import BaseConverter


class ManiacontrolConverter(BaseConverter):
	"""
	The Maniacontrol Converter uses MySQL to convert the data to the new PyPlanet structure.

	Please take a look at :doc:`Migrating from other controllers </convert/index>` pages for information on how to use
	this.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.player_cache = dict()
		self.map_cache = dict()

		if not self.prefix:
			self.prefix = 'mc_'

	async def migrate(self, _):
		print('Migrating players...')
		await self.migrate_players()

		print('Migrating maps...')
		await self.migrate_maps()

		print('Migrating records...')
		await self.migrate_local_records()

		print('Migrating karma...')
		await self.migrate_karma()

	async def migrate_players(self):
		with self.connection.cursor() as cursor:
			cursor.execute('SELECT * FROM {prefix}players'.format(prefix=self.prefix))
			for s_player in cursor.fetchall():
				# Check if we already have this player in our database. If we have, ignore and print message.
				try:
					player = await Player.get_by_login(s_player['login'])
					self.player_cache[player.login] = player

					print('Player with login \'{}\' already exists, skipping..'.format(s_player['login']))
					continue
				except:
					# Not found, create it:
					player = await Player.create(
						login=s_player['login'], nickname=s_player['nickname'],
						last_seen=s_player['changed'],
					)
					self.player_cache[player.login] = player

	async def migrate_maps(self):
		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT * '
				'FROM {prefix}maps '.format(prefix=self.prefix)
			)
			for s_map in cursor.fetchall():
				# Check if we already have this map in our database. If we have, ignore and print message.
				try:
					map_instance = await Map.get_by_uid(s_map['uid'])
					self.map_cache[map_instance.uid] = map_instance

					print('Map with uid \'{}\' already exists, skipping..'.format(s_map['uid']))
					continue
				except:
					# Not found, create it:
					map_instance = await Map.create(
						uid=s_map['uid'], name=s_map['name'], file=s_map['fileName'], author_login=s_map['authorLogin'],
						environment=s_map['environment'], map_type=s_map['mapType'],
					)
					self.map_cache[map_instance.uid] = map_instance

	async def migrate_local_records(self):
		if 'local_records' not in self.instance.apps.apps:
			print('Skipping local records. App not activated!')
			return

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					'SELECT 1 FROM {prefix}localrecords'.format(prefix=self.prefix)
				)
				result = cursor.fetchone()
				if not result:
					raise Exception()
			except:
				print('Local records table not found! Skipping...')
				return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT record.*, map.uid, player.login '
				'FROM {prefix}localrecords as record, {prefix}maps as map, {prefix}players as player '
				'WHERE record.mapIndex = map.index AND record.playerIndex = player.index '.format(
					prefix=self.prefix
				)
			)
			for s_record in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_record['uid']] if s_record['uid'] in self.map_cache else await Map.get(uid=s_record['uid'])
					player = self.player_cache[s_record['login']] if s_record['login'] in self.player_cache else await Player.get(login=s_record['login'])
				except:
					# Skip.
					print('Can\'t convert record, map or player not found. Skipping...')
					continue

				try:
					await LocalRecord.get(map=map, player=player)
					print('Record with uid \'{}\' and player \'{}\' already exists, skipping..'.format(map.uid, player.login))
				except:
					await LocalRecord.create(
						map=map, player=player, score=s_record['time'], checkpoints=s_record['checkpoints'],
						created_at=s_record['changed'], updated_at=datetime.datetime.now()
					)

	async def migrate_karma(self):
		if 'karma' not in self.instance.apps.apps:
			print('Skipping karma. App not activated!')
			return

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					'SELECT 1 FROM {prefix}karma'.format(prefix=self.prefix)
				)
				result = cursor.fetchone()
				if not result:
					raise Exception()
			except:
				print('Karma table not found! Skipping...')
				return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT rating.*, map.uid, player.login '
				'FROM {prefix}karma AS rating, {prefix}maps AS map, {prefix}players AS player '
				'WHERE rating.mapIndex = map.index AND rating.playerIndex = player.index'.format(
					prefix=self.prefix
				)
			)
			for s_karma in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_karma['uid']] if s_karma['uid'] in self.map_cache else await Map.get(uid=s_karma['uid'])
					player = self.player_cache[s_karma['login']] if s_karma['login'] in self.player_cache else await Player.get(login=s_karma['login'])
				except:
					# Skip.
					print('Can\'t convert karma, map or player not found. Skipping...')
					continue

				if s_karma['vote'] == 0:
					continue

				try:
					await Karma.get(map=map, player=player)
					print('Karma with uid \'{}\' and player \'{}\' already exists, skipping..'.format(map.uid, player.login))
				except:
					await Karma.create(
						map=map, player=player, score=-1 if s_karma['vote'] < 0 else 1,
						updated_at=datetime.datetime.now()
					)
