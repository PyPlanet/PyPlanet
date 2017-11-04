import datetime

from pyplanet.apps.contrib.karma.models import Karma
from pyplanet.apps.contrib.local_records.models import LocalRecord
from pyplanet.apps.core.maniaplanet.models import Player, Map
from pyplanet.contrib.converter.base import BaseConverter


class ExpansionConverter(BaseConverter):
	"""
	The eXpansion Converter uses MySQL to convert the data to the new PyPlanet structure.

	Please take a look at :doc:`Migrating from other controllers </convert/index>` pages for information on how to use
	this.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.player_cache = dict()
		self.map_cache = dict()

		if not self.prefix:
			self.prefix = 'exp_'

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
					player = await Player.get_by_login(s_player['player_login'])
					self.player_cache[player.login] = player

					print('Player with login \'{}\' already exists, skipping..'.format(s_player['player_login']))
					continue
				except:
					last_seen = None

					# Not found, create it:
					player = await Player.create(
						login=s_player['player_login'], nickname=s_player['player_nickname'],
						last_seen=last_seen,
					)
					self.player_cache[player.login] = player

	async def migrate_maps(self):
		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT * '
				'FROM {prefix}maps'.format(prefix=self.prefix)
			)
			for s_map in cursor.fetchall():
				# Check if we already have this map in our database. If we have, ignore and print message.
				try:
					map_instance = await Map.get_by_uid(s_map['challenge_uid'])
					self.map_cache[map_instance.uid] = map_instance

					print('Map with uid \'{}\' already exists, skipping..'.format(s_map['challenge_uid']))
					continue
				except:
					# Not found, create it:
					map_instance = await Map.create(
						uid=s_map['challenge_uid'], name=s_map['challenge_name'], file=s_map['challenge_file'],
						author_login=s_map['challenge_author'], environment=s_map['challenge_environment'],
						map_type=None, map_style=None, num_checkpoints=None, price=s_map['challenge_copperPrice'],
						num_laps=s_map['challenge_nbLaps'] if int(s_map['challenge_lapRace']) == 1 else None,
						time_author=s_map['challenge_authorTime'], time_bronze=s_map['challenge_bronzeTime'],
						time_silver=s_map['challenge_silverTime'], time_gold=s_map['challenge_goldTime'],
					)
					self.map_cache[map_instance.uid] = map_instance

	async def migrate_local_records(self):
		if 'local_records' not in self.instance.apps.apps:
			print('Skipping local records. App not activated!')
			return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT * '
				'FROM {prefix}records '.format(
					prefix=self.prefix
				)
			)
			for s_record in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_record['record_challengeuid']] \
						if s_record['record_challengeuid'] in self.map_cache \
						else await Map.get(uid=s_record['record_challengeuid'])
					player = self.player_cache[s_record['record_playerlogin']] \
						if s_record['record_playerlogin'] in self.player_cache \
						else await Player.get(login=s_record['record_playerlogin'])
				except:
					# Skip.
					print('Can\'t convert record, map or player not found. Skipping...')
					continue

				try:
					await LocalRecord.get(map=map, player=player)
					print('Record with uid \'{}\' and player \'{}\' already exists, skipping..'.format(map.uid, player.login))
				except:
					created_at = datetime.datetime.fromtimestamp(s_record['record_date'])
					await LocalRecord.create(
						map=map, player=player, score=s_record['record_score'], checkpoints=s_record['record_checkpoints'],
						created_at=created_at, updated_at=datetime.datetime.now()
					)

	async def migrate_karma(self):
		if 'karma' not in self.instance.apps.apps:
			print('Skipping karma. App not activated!')
			return

		with self.connection.cursor() as cursor:
			cursor.execute(
				'SELECT * '
				'FROM {prefix}ratings '.format(
					prefix=self.prefix
				)
			)
			for s_karma in cursor.fetchall():
				# Get map + player
				try:
					map = self.map_cache[s_karma['uid']] \
						if s_karma['uid'] in self.map_cache \
						else await Map.get(uid=s_karma['uid'])
					player = self.player_cache[s_karma['login']] \
						if s_karma['login'] in self.player_cache \
						else await Player.get(login=s_karma['login'])
				except:
					# Skip.
					print('Can\'t convert karma, map or player not found. Skipping...')
					continue

				if s_karma['rating'] == 0:
					continue

				try:
					await Karma.get(map=map, player=player)
					print('Karma with uid \'{}\' and player \'{}\' already exists, skipping..'.format(map.uid, player.login))
				except:
					await Karma.create(
						map=map, player=player, score=-1 if s_karma['rating'] < 3 else 1,
						updated_at=datetime.datetime.now()
					)
