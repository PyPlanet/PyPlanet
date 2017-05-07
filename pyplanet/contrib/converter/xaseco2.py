import datetime

from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.contrib.local_records.models import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Player, Map
from pyplanet.apps.core.statistics.models import Score
from pyplanet.contrib.converter.base import BaseConverter


class Xaseco2Converter(BaseConverter):
	"""
	The XAseco2 Converter uses MySQL to convert the data to the new PyPlanet structure.
	
	Please take a look at :doc:`Migrating from other controllers </convert/index>` pages for information on how to use
	this.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.player_cache = dict()
		self.map_cache = dict()

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
			cursor.execute('SELECT * FROM players')
			for s_player in cursor.fetchall():
				# Check if we already have this player in our database. If we have, ignore and print message.
				try:
					player = await Player.get_by_login(s_player['Login'])
					self.player_cache[player.login] = player

					print('Player with login \'{}\' already exists, skipping..'.format(s_player['Login']))
					continue
				except:
					# Not found, create it:
					player = await Player.create(
						login=s_player['Login'], nickname=s_player['NickName']
					)
					self.player_cache[player.login] = player

	async def migrate_maps(self):
		with self.connection.cursor() as cursor:
			cursor.execute('SELECT * FROM maps')
			for s_map in cursor.fetchall():
				# Check if we already have this player in our database. If we have, ignore and print message.
				try:
					map_instance = await Map.get_by_uid(s_map['Uid'])
					self.map_cache[map_instance.uid] = map_instance

					print('Map with uid \'{}\' already exists, skipping..'.format(s_map['Uid']))
					continue
				except:
					# Not found, create it:
					# HACK: We don't know the file yet. Empty string to fill until pyplanet has started next time.
					map_instance = await Map.create(
						uid=s_map['Uid'], name=s_map['Name'], file='', author_login=s_map['Author'],
						environment=s_map['Environment']
					)
					self.map_cache[map_instance.uid] = map_instance

	async def migrate_local_records(self):
		if 'local_records' not in self.instance.apps.apps:
			print('Skipping local records. App not activated!')
			return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT records.*, maps.Uid, players.Login '
				'FROM records, maps, players '
				'WHERE records.MapId = maps.Id AND records.PlayerId = players.Id'
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
				'SELECT rs_karma.*, maps.Uid, players.Login '
				'FROM rs_karma, maps, players '
				'WHERE rs_karma.MapId = maps.Id AND rs_karma.PlayerId = players.Id'
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
				'SELECT rs_times.*, maps.Uid, players.Login '
				'FROM rs_times, maps, players '
				'WHERE rs_times.MapId = maps.Id AND rs_times.PlayerId = players.Id'
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
						map=map, player=player, score=s_time['Score'], created_at=datetime.datetime.fromtimestamp(s_time['Date'])
					)
					print('Score with uid \'{}\', player \'{}\', score \'{}\' at \'{}\' already exists, skipping..'.format(
						map.uid, player.login, s_time['Score'], s_time['Date'],
					))
				except:
					await Score.create(
						map=map, player=player, score=s_time['Score'], checkpoints=s_time['Checkpoints'],
						created_at=datetime.datetime.fromtimestamp(s_time['Date']),
					)
