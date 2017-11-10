import datetime

from pyplanet.apps.core.maniaplanet.models import Player, Map
from pyplanet.apps.contrib.jukebox.views import FolderListView, FolderMapListView

from .models import MapFolder as Folders, MapInFolder


class FolderManager:
	def __init__(self, app):
		self.app = app

		# Initiate global folders.
		self.auto_folders = list()
		self.public_folders = list()

	async def on_start(self):
		"""
		Called after startup of PyPlanet so it can investigate the automatic folders.

		:return:
		"""
		self.auto_folders = list()

		self.auto_folders.append({'id': 'newest', 'name': 'Newest maps (last 14 days)', 'owner': 'PyPlanet', 'type': 'auto'})

		if 'local_records' in self.app.instance.apps.apps:
			self.auto_folders.append({'id': 'local_none', 'name': 'Map record: none', 'owner': 'PyPlanet', 'type': 'auto'})
			self.auto_folders.append({'id': 'length_shorter_30s', 'name': 'Map record: below 30 seconds', 'owner': 'PyPlanet', 'type': 'auto'})
			self.auto_folders.append({'id': 'length_longer_60s', 'name': 'Map record: above 60 seconds', 'owner': 'PyPlanet', 'type': 'auto'})

		if 'karma' in self.app.instance.apps.apps:
			self.auto_folders.append({'id': 'karma_none', 'name': 'Map karma: no votes', 'owner': 'PyPlanet', 'type': 'auto'})
			self.auto_folders.append({'id': 'karma_negative', 'name': 'Map karma: negative', 'owner': 'PyPlanet', 'type': 'auto'})
			self.auto_folders.append({'id': 'karma_undecided', 'name': 'Map karma: undecided', 'owner': 'PyPlanet', 'type': 'auto'})
			self.auto_folders.append({'id': 'karma_positive', 'name': 'Map karma: positive', 'owner': 'PyPlanet', 'type': 'auto'})

	async def get_folders(self, player):
		"""
		Get the folders, as combined object, for the specific player.

		:param player: Player instance
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return:
		"""
		# Fetch the public or private folders of the users.
		raw_list = await Folders.objects.execute(
			Folders.select(Folders, Player)
				.join(Player)
				.where((Player.login == player.login) | (Folders.public == True))
				.order_by(Folders.public.desc())
		)

		# Convert to the wanted objects.
		folder_list = list()
		folder_list.extend(self.auto_folders.copy())

		for folder in raw_list:
			folder_id = 'database_{}'.format(folder.get_id())
			folder_list.append(
				{
					'id': folder_id, 'name': folder.name, 'owner_login': folder.player.login,
					'owner': folder.player.nickname, 'type': 'public' if folder.public else 'private'
				}
			)

		return folder_list

	async def get_private_folders(self, player):
		"""
		Get the private folders of the given player.

		:param player: Player instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return:
		"""
		return await Folders.objects.execute(
			Folders.select(Folders, Player)
				.join(Player)
				.where((Player.login == player.login) & (Folders.public == False))
		)

	async def get_writable_folders(self, player):
		"""
		Get writable folders for the given player.

		:param player: Player instance
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		:return: List with writable folders.
		"""
		if player.level >= player.LEVEL_ADMIN:
			return await Folders.objects.execute(
				Folders.select(Folders, Player)
					.join(Player)
					.where((Player.login == player.login) | (Folders.public == True))
			)

		return await Folders.objects.execute(
			Folders.select(Folders, Player)
				.join(Player)
				.where((Player.login == player.login))
		)

	async def create_folder(self, **kwargs):
		"""
		Create folder, based on the paramters given.

		:param kwargs:
		:return: Folder instance.
		"""
		folder = Folders(**kwargs)
		await folder.save()
		return folder

	async def display_folder_list(self, player):
		"""
		Create folder listview, display and return instance.

		:param player:
		:return:
		"""
		view = FolderListView(self, player)
		await view.display(player=player)
		return view

	async def get_folder_code_contents(self, folder_code):
		folder = folder_code

		map_list = []
		fields = []
		folder_instance = None

		if folder['id'] == 'newest':
			filter_from = datetime.datetime.now() - datetime.timedelta(days=14)
			map_list = [m for m in self.app.instance.map_manager.maps if m.created_at > filter_from]
		elif folder['id'] == 'local_none':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'local') and m.local['record_count'] == 0]
		elif folder['id'] == 'length_shorter_30s':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'local') and m.local['first_record'] is not None and m.local['first_record'].score < 30000]
		elif folder['id'] == 'length_longer_60s':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'local') and m.local['first_record'] is not None and m.local['first_record'].score > 60000]
		elif folder['id'] == 'karma_none':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['vote_count'] is 0]
		elif folder['id'] == 'karma_negative':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['map_karma'] < 0]
		elif folder['id'] == 'karma_undecided':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['map_karma'] == 0]
		elif folder['id'] == 'karma_positive':
			map_list = [m for m in self.app.instance.map_manager.maps if hasattr(m, 'karma') and m.karma['map_karma'] > 0]
		elif folder['id'].startswith('database_'):
			# Get the real folder model instance.
			folder_instance = await Folders.get(id=int(folder['id'].replace('database_', '')))

			# Personal folder from database
			maps_in_folder = [m.map.uid for m in await MapInFolder.objects.execute(
				MapInFolder.select(MapInFolder, Map)
					.join(Map)
					.where(MapInFolder.folder == int(folder['id'].replace('database_', '')))
			)]

			map_list = [m for m in self.app.instance.map_manager.maps if m.uid in maps_in_folder]

		if folder['id'].startswith('length_') or folder['id'].startswith('database_'):
			fields.append({
				'name': 'Local Record',
				'index': 'local_record',
				'sorting': True,
				'searching': False,
				'width': 40,
			})

		if folder['id'].startswith('karma_') or folder['id'].startswith('database_'):
			fields.append({
				'name': 'Karma',
				'index': 'karma',
				'sorting': True,
				'searching': False,
				'width': 20,
			})

		return fields, map_list, folder, folder_instance

	async def display_folder(self, player, folder_code):
		# Initiate folder contents list view.
		view = FolderMapListView(self, folder_code, player)
		await view.display(player=player)
