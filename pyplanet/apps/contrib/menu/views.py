from pyplanet.views.generics.widget import TemplateView
from pyplanet import __version__ as version
from pyplanet.apps.contrib.menu.signals import menu_add_entry, menu_remove_entry
import json
import uuid


class MenuView(TemplateView):
	template_name = 'menu/menu2.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(app.context.ui, *args, **kwargs)
		self.app = app
		self.manager = app.context.ui
		self.id = 'menu'
		self.menu = [
			{
				"icon": "🎮",
				"category": "Generic",
				"level": 0,
				"submenu": []
			},
			{
				"icon": "",
				"category": "Votes",
				"level": 0,
				"submenu": []
			},
			{
				"icon": "",
				"category": "Maps",
				"level": 2,
				"submenu": []
			},
			{
				"icon": "",
				"category": "Settings",
				"level": 3,
				"submenu": []
			}
		]

		self.app.context.signals.listen(menu_add_entry, self.add_from_signal)
		self.add_item("", "Map list", "Generic", 0, self.action_maps)
		self.add_item("⏳", "Jukebox", "Generic", 0, self.action_jukebox)
		self.add_item("👥", "Players", "Generic", 0, self.action_players)

		self.add_item("", "Vote Replay", "Votes", 0, self.action_vote_restart)
		self.add_item("🕑", "Vote Extend Time", "Votes", 0, self.action_vote_extend)
		self.add_item("", "Vote Skip", "Votes", 0, self.action_vote_skip)
		self.add_item("✗", "Cancel Vote", "Votes", 2, self.action_vote_adm_cancel)
		self.add_item("✓", "Pass Vote", "Votes", 2, self.action_vote_adm_pass)

		self.add_item("", "Skip", "Maps", 2, self.action_adm_skip)
		self.add_item("", "Replay", "Maps", 2, self.action_adm_replay)
		self.add_item("", "Restart", "Maps", 2, self.action_adm_res)
		self.add_item("", "Previous", "Maps", 2, self.action_adm_prev)
		self.add_item("", "End round", "Maps", 2, self.action_adm_er)
		self.add_item("", "Shuffle maps", "Maps", 3, self.action_adm_shuffle)

		self.add_item("", "Script settings", "Settings", 2, self.action_adm_mode)
		self.add_item("", "PyPlanet settings", "Settings", 2, self.action_adm_settings)
		self.add_item("", "Script settings", "Settings", 3, self.action_adm_server)

	async def get_context_data(self):
		context = await super().get_context_data()
		context['player_level'] = 0
		context['version'] = version
		return context

	async def get_per_player_data(self, login):
		data = await super().get_per_player_data(login)
		data['player_level'] = 0
		player = await self.app.instance.player_manager.get_player(login)
		if player:
			data['player_level'] = player.level
		data['json'] = self.get_menu(data['player_level'])
		return data

	async def add_from_signal(self, source, signal):
		self.add_item(source["icon"], source["menu_item"], source["category"], source["level"], source["callback"])
		await self.display()

	def add_item(self, icon="n", menu_item="none", category="Generic", level=0, callback=None):
		for key, item in enumerate(self.menu):
			if item["category"] == category:
				if callback is not None:
					uid = uuid.uuid4().hex
					self.subscribe(uid, callback)
					self.menu[key]["submenu"].append([icon, menu_item, uid, level])

	async def action_jukebox(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/jukebox list')

	async def action_vote_skip(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/skip')

	async def action_vote_restart(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/res')

	async def action_vote_extend(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/extend')

	async def action_vote_adm_cancel(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//cancel')

	async def action_vote_adm_pass(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//pass')

	async def action_maps(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '/list')

	async def action_players(self, player, *args, **kwargs):
		if player.level == 0:
			return await self.app.instance.command_manager.execute(player, '/players')
		else:
			return await self.app.instance.command_manager.execute(player, '//players')

	async def action_adm_skip(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//skip')

	async def action_adm_res(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//res')

	async def action_adm_prev(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//prev')

	async def action_adm_replay(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//replay')

	async def action_adm_er(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//endround')

	async def action_adm_server(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//server')

	async def action_adm_mode(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//modesettings')

	async def action_adm_settings(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//settings')

	async def action_adm_players(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//players')

	async def action_adm_shuffle(self, player, *args, **kwargs):
		return await self.app.instance.command_manager.execute(player, '//shuffle')

	def get_menu(self, player_level):
		data = []
		for item in self.menu:
			sub = []
			for submenu in item['submenu']:
				if player_level >= submenu[3]:
					sub.append(submenu)
			item['submenu'] = sub
			if player_level >= item['level']:
				data.append(item)
		return json.dumps(data, sort_keys=True, indent=2)
