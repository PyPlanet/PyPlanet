import logging
import os
from argparse import Namespace

from pyplanet.views.generics import ManualListView
from pyplanet.utils import gbxparser

logger = logging.getLogger(__name__)


class BrowserView(ManualListView):
	app = None
	title = 'Local Maps'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	data = []

	def __init__(self, app, player):
		super().__init__(self)
		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.objects_raw = []
		self.current_dir = ''

		self.fields = self.create_fields()

		self.sort_field = self.fields[0]

	async def set_dir(self, directory):
		self.objects_raw = list()
		self.current_dir = directory
		self.title = 'Local Maps     $n$aaa' + self.current_dir

		full_dir = os.path.join('UserData', 'Maps', self.current_dir)
		files = await self.app.instance.storage.driver.listdir(path=full_dir)

		self.objects_raw.append({'icon': '$ff0D', 'file_name': '..'})

		# Add the files to the directory list.
		for file in files:
			is_file = await self.app.instance.storage.driver.is_file(os.path.join(full_dir, file))
			if is_file and not file.lower().endswith('map.gbx'):
				continue
			self.objects_raw.append({'icon': 'F' if is_file else '$ff0D', 'file_name': file})
		await self.display(player=self.player.login)

	def create_fields(self):
		return [
			{
				'name': 'T',
				'index': 'icon',
				'sorting': True,
				'searching': False,
				'width': 10,
				'type': 'label'
			},
			{
				'name': 'Name',
				'index': 'file_name',
				'sorting': True,
				'searching': True,
				'width': 150,
				'type': 'label',
				'action': self.action_file
			},
		]

	async def get_fields(self):
		return self.fields

	async def action_file(self, player, values, instance, **kwargs):
		isdir = instance['icon'] == '$ff0D'
		filename = instance['file_name']
		if isdir:
			if filename == '..':
				await self.set_dir(os.path.dirname(self.current_dir))
			else:
				await self.set_dir(os.path.join(self.current_dir, filename))
		else:
			await self.add_map(filename, player)

	async def add_map(self, filename, player):
		map_path = os.path.join(self.current_dir, filename)

		data = Namespace()
		data.map = map_path
		await self.app.map.add_local_map(player, data)
