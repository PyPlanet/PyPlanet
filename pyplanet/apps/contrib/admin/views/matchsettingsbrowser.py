import logging
import os
import asyncio
import xml.etree.ElementTree as ET

from argparse import Namespace
from pyplanet.views.generics import ManualListView
from pyplanet.utils import gbxparser

logger = logging.getLogger(__name__)


class LoadMatchSettingsBrowserView(ManualListView):
	app = None
	title = 'Local MatchSettings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	data = []

	def __init__(self, app, player):
		super().__init__(self)
		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False
		self.objects_raw = []
		self.current_dir = ''

		self.fields = self.create_fields()

		self.sort_field = self.fields[0]

	async def set_dir(self, directory):
		self.objects_raw = list()
		self.current_dir = directory
		self.title = 'Local MatchSettings     $n$aaa' + self.current_dir

		full_dir = os.path.join('UserData', 'Maps/MatchSettings', self.current_dir)
		files = await self.app.instance.storage.driver.listdir(path=full_dir)
		self.objects_raw.append({'icon': '$ff0D', 'file_name': '..'})

		# Add the files to the directory list.
		for file in files:
			is_file = await self.app.instance.storage.driver.is_file(os.path.join(full_dir, file))
			if is_file and not file.lower().endswith('.txt'):
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
			await self.load_matchsettings(filename, player)

	async def load_matchsettings(self, filename, player):
		map_path = os.path.join(self.current_dir, filename)
				
		try:
			file_path = 'MatchSettings/{}'.format(filename)
			map_dir = await self.app.instance.gbx('GetMapsDirectory')
			tree = ET.parse(map_dir+file_path)
			root = tree.getroot()
			
			# We need to go one level below to get <header>
			# and then one more level from that to go to <type>
			for script_name in root.findall('gameinfos/script_name'):
				await self.app.instance.mode_manager.set_next_script(script_name.text)
				await self.app.instance.mode_manager.get_next_script(True)			
			for entry in root.findall('mode_script_settings'):
				settings = entry.findall('setting')
				for setting in settings:
					settings_modescript_name = dict()
					settings_modescript_name = setting.attrib['name']
					settings_modescript_type = setting.attrib['type']
					if settings_modescript_type == 'boolean':
						real_type = bool
					elif settings_modescript_type == 'integer':
						real_type = int
					elif settings_modescript_type == 'double':
						real_type = float
					elif settings_modescript_type == 'text':
						real_type = str

					settings_modescript_value = real_type(setting.attrib['value'])
					modescriptsettings = {settings_modescript_name: settings_modescript_value}
					await self.app.instance.mode_manager.update_next_settings(modescriptsettings)
		except Exception as e:
			logger.warning('Error when script settings are being changed: {}'.format(player.login, str(e)))
			message_mode_scriptsettings = '$ff0Error: Can\'t SetScriptSettings, Error: {}'.format(str(e))
			await self.app.instance.chat(message_mode_scriptsettings, player.login)
		
		try:
			await self.app.instance.map_manager.load_matchsettings(file_path)
			message = '$ff0Match Settings has been loaded from: {}'.format(file_path)
			message_mode_scriptsettings = '$ff0Mode Script Settings has been loaded from: {}'.format(file_path)
		except:
			message = '$ff0Could not load match settings! Does the file exists? Check log for details.'
			message_mode_scriptsettings = '$ff0Could not load Mode Script Settings!  Check log for details.'
			
		# Send message + reload all maps in memory.
		await asyncio.gather(
				self.app.instance.chat(message, player),
				self.app.instance.chat(message_mode_scriptsettings, player),
				self.app.instance.map_manager.update_list(full_update=True)
				)
		
class WriteMatchSettingsBrowserView(ManualListView):
	app = None
	title = 'Local MatchSettings'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	data = []

	def __init__(self, app, player):
		super().__init__(self)
		self.app = app
		self.player = player
		self.manager = app.context.ui
		self.provide_search = False
		self.objects_raw = []
		self.current_dir = ''

		self.fields = self.create_fields()

		self.sort_field = self.fields[0]

	async def set_dir(self, directory):
		self.objects_raw = list()
		self.current_dir = directory
		self.title = 'Local MatchSettings     $n$aaa' + self.current_dir

		full_dir = os.path.join('UserData', 'Maps/MatchSettings', self.current_dir)
		files = await self.app.instance.storage.driver.listdir(path=full_dir)
		self.objects_raw.append({'icon': '$ff0D', 'file_name': '..'})

		# Add the files to the directory list.
		for file in files:
			is_file = await self.app.instance.storage.driver.is_file(os.path.join(full_dir, file))
			if is_file and not file.lower().endswith('.txt'):
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
			await self.write_matchsettings(filename, player)

	async def write_matchsettings(self, filename, player):
		map_path = os.path.join(self.current_dir, filename)

		data = Namespace()
		data.file = map_path
		await self.app.map.write_map_list(player, data)
