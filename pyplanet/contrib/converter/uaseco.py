import datetime

from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.contrib.local_records.models import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Player, Map
from pyplanet.apps.core.statistics.models import Score
from pyplanet.contrib.converter.base import BaseConverter


class UasecoConverter(BaseConverter):
	"""
	The UAseco Converter uses MySQL to convert the data to the new PyPlanet structure.

	Please take a look at :doc:`Migrating from other controllers </convert/index>` pages for information on how to use
	this.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.player_cache = dict()
		self.map_cache = dict()

		if not self.prefix:
			self.prefix = 'uaseco_'

	async def migrate(self, _):
		print('Migrating players...')
		await self.migrate_players()

		print('Migrating maps...')
		await self.migrate_maps()

		print('Migrating records...')
		await self.migrate_local_records()

		print('Migrating karma...')
		await self.migrate_karma()

		print('Migrating times...')
		await self.migrate_times()

	async def migrate_players(self):
		with self.connection.cursor() as cursor:
			cursor.execute('SELECT * FROM {prefix}players'.format(prefix=self.prefix))
			for s_player in cursor.fetchall():
				# Check if we already have this player in our database. If we have, ignore and print message.
				try:
					player = await Player.get_by_login(s_player['Login'])
					self.player_cache[player.login] = player

					print('Player with login \'{}\' already exists, skipping..'.format(s_player['Login']))
					continue
				except:
					try:
						last_seen = datetime.datetime.strptime(s_player['LastVisit'], '%Y-%m-%d %H:%M:%S')
					except:
						last_seen = None

					# Not found, create it:
					player = await Player.create(
						login=s_player['Login'], nickname=s_player['Nickname'],
						last_seen=last_seen,
					)
					self.player_cache[player.login] = player

	async def migrate_maps(self):
		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT map.*, author.Login as Author '
				'FROM {prefix}maps as map '
				'JOIN {prefix}authors as author ON map.AuthorId = author.AuthorId'.format(prefix=self.prefix)
			)
			for s_map in cursor.fetchall():
				# Check if we already have this map in our database. If we have, ignore and print message.
				try:
					map_instance = await Map.get_by_uid(s_map['Uid'])
					self.map_cache[map_instance.uid] = map_instance

					print('Map with uid \'{}\' already exists, skipping..'.format(s_map['Uid']))
					continue
				except:
					# Not found, create it:
					map_instance = await Map.create(
						uid=s_map['Uid'], name=s_map['Name'], file=s_map['Filename'], author_login=s_map['Author'],
						environment=s_map['Environment'], map_type=s_map['Type'], map_style=s_map['Style'],
						num_laps=s_map['NbLaps'] if s_map['MultiLap'] == 'true' else None,
						num_checkpoints=s_map['NbCheckpoints'], price=s_map['Cost'],
						time_author=s_map['AuthorTime'], time_bronze=s_map['BronzeTime'],
						time_silver=s_map['SilverTime'], time_gold=s_map['GoldTime'],
					)
					self.map_cache[map_instance.uid] = map_instance

	async def migrate_local_records(self):
		if 'local_records' not in self.instance.apps.apps:
			print('Skipping local records. App not activated!')
			return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT record.*, map.Uid, player.Login '
				'FROM {prefix}records as record, {prefix}maps as map, {prefix}players as player '
				'WHERE record.MapId = map.MapId AND record.PlayerId = player.PlayerId'.format(
					prefix=self.prefix
				)
			)
			for s_record in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_record['Uid']] if s_record['Uid'] in self.map_cache else await Map.get(uid=s_record['Uid'])
					player = self.player_cache[s_record['Login']] if s_record['Login'] in self.player_cache else await Player.get(login=s_record['Login'])
				except:
					# Skip.
					print('Can\'t convert record, map or player not found. Skipping...')
					continue

				try:
					await LocalRecord.get(map=map, player=player)
					print('Record with uid \'{}\' and player \'{}\' already exists, skipping..'.format(map.uid, player.login))
				except:
					await LocalRecord.create(
						map=map, player=player, score=s_record['Score'], checkpoints=s_record['Checkpoints'],
						created_at=s_record['Date'], updated_at=datetime.datetime.now()
					)

	async def migrate_karma(self):
		if 'karma' not in self.instance.apps.apps:
			print('Skipping karma. App not activated!')
			return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT rating.*, map.Uid, player.Login '
				'FROM {prefix}ratings AS rating, {prefix}maps AS map, {prefix}players AS player '
				'WHERE rating.MapId = map.MapId AND rating.PlayerId = player.PlayerId'.format(
					prefix=self.prefix
				)
			)
			for s_karma in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_karma['Uid']] if s_karma['Uid'] in self.map_cache else await Map.get(uid=s_karma['Uid'])
					player = self.player_cache[s_karma['Login']] if s_karma['Login'] in self.player_cache else await Player.get(login=s_karma['Login'])
				except:
					# Skip.
					print('Can\'t convert karma, map or player not found. Skipping...')
					continue

				if s_karma['Score'] == 0:
					continue

				try:
					await Karma.get(map=map, player=player)
					print('Karma with uid \'{}\' and player \'{}\' already exists, skipping..'.format(map.uid, player.login))
				except:
					await Karma.create(
						map=map, player=player, score=-1 if s_karma['Score'] < 0 else 1,
						updated_at=datetime.datetime.now()
					)

	async def migrate_times(self):
		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT score.*, map.Uid, player.Login '
				'FROM {prefix}times AS score, {prefix}maps AS map, {prefix}players AS player '
				'WHERE score.MapId = map.MapId AND score.PlayerId = player.PlayerId'.format(
					prefix=self.prefix
				)
			)
			for s_time in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_time['Uid']] if s_time['Uid'] in self.map_cache else await Map.get(uid=s_time['Uid'])
					player = self.player_cache[s_time['Login']] if s_time['Login'] in self.player_cache else await Player.get(login=s_time['Login'])
				except:
					# Skip.
					print('Can\'t convert time, map or player not found. Skipping...')
					continue

				if s_time['Score'] == 0:
					continue

				try:
					await Score.get(
						map=map, player=player, score=s_time['Score'], created_at=s_time['Date']
					)
					print('Score with uid \'{}\', player \'{}\', score \'{}\' at \'{}\' already exists, skipping..'.format(
						map.uid, player.login, s_time['Score'], s_time['Date'],
					))
				except:
					await Score.create(
						map=map, player=player, score=s_time['Score'], checkpoints=s_time['Checkpoints'],
						created_at=s_time['Date'],
					)
