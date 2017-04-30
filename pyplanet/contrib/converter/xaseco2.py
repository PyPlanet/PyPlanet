import datetime

from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.contrib.local_records.models import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Player, Map
from pyplanet.contrib.converter.base import BaseConverter


class Xaseco2Converter(BaseConverter):
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
			cursor.execute('SELECT * FROM players')
			for s_player in cursor.fetchall():
				# Check if we already have this player in our database. If we have, ignore and print message.
				try:
					await Player.get_by_login(s_player['Login'])

					print('Player with login \'{}\' already exists, skipping..'.format(s_player['Login']))
					continue
				except:
					# Not found, create it:
					await Player.create(
						login=s_player['Login'], nickname=s_player['NickName']
					)

	async def migrate_maps(self):
		with self.connection.cursor() as cursor:
			cursor.execute('SELECT * FROM maps')
			for s_map in cursor.fetchall():
				# Check if we already have this player in our database. If we have, ignore and print message.
				try:
					await Map.get_by_uid(s_map['Uid'])

					print('Map with uid \'{}\' already exists, skipping..'.format(s_map['Uid']))
					continue
				except:
					# Not found, create it:
					# HACK: We don't know the file yet. Empty string to fill until pyplanet has started next time.
					await Map.create(
						uid=s_map['Uid'], name=s_map['Name'], file='', author_login=s_map['Author'],
						environment=s_map['Environment']
					)

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
					map = await Map.get(uid=s_record['Uid'])
					player = await Player.get(login=s_record['Login'])
				except:
					# Skip.
					print('Can\'t convert record, map or player not found. Skipping...')
					continue

				await LocalRecord.get_or_create(
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
					map = await Map.get(uid=s_karma['Uid'])
					player = await Player.get(login=s_karma['Login'])
				except:
					# Skip.
					print('Can\'t convert karma, map or player not found. Skipping...')
					continue

				if s_karma['Score'] == 0:
					continue

				await Karma.get_or_create(
					map=map, player=player, score=-1 if s_karma['Score'] < 0 else 1,
					updated_at=datetime.datetime.now()
				)
