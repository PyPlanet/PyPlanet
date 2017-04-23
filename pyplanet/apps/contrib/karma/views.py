from pyplanet.apps.core.maniaplanet.models import Map

from pyplanet.views.generics.list import ListView, ManualListView


class SampleManualListView(ManualListView):
	title = 'Map List Testing'
	icon_style = 'Icons64x64_1'
	icon_substyle = 'Browser'

	async def get_data(self):
		return [
			{'name': 'Test', 'author_login': 'Test Login'},
			{'name': 'Abc', 'author_login': 'Test Login'},
			{'name': 'Cba', 'author_login': 'Test Login'},
			{'name': 'gadg', 'author_login': 'Test Login'},
			{'name': 'hjysdt', 'author_login': 'Test Login'},
			{'name': 'uyasedgf', 'author_login': 'Test Login'},
			{'name': 'dafklug', 'author_login': 'Test Login'},
			{'name': 'asdgadf', 'author_login': 'Test Login'},
			{'name': 'adfgt7y', 'author_login': 'Test Login'},
			{'name': 'hgnvc', 'author_login': 'Test Login'},
			{'name': 'tyucgh', 'author_login': 'Test Login'},
			{'name': 'qwerqwer', 'author_login': 'Test Login'},
			{'name': 'fj', 'author_login': 'Test Login'},
			{'name': 'qwecbvncbvnrqwer', 'author_login': 'Test Login'},
			{'name': 'cbvnjhk', 'author_login': 'Test Login 2'},
			{'name': 'sergcvbx', 'author_login': 'Test Login'},
			{'name': 'zsdaeregt', 'author_login': 'Test Login'},
			{'name': 'utyaaa', 'author_login': 'Test Login'},
			{'name': 'fsdghxcvbdgf', 'author_login': 'Test Login'},
			{'name': 'asasaaaa', 'author_login': 'Test Login'},
			{'name': 'tyutyuew', 'author_login': 'Test Login'},
			{'name': 'asdfiii', 'author_login': 'Test Login'},
			{'name': 'ertw6422', 'author_login': 'Test Login'},
			{'name': 'w57245646', 'author_login': 'Test Login'},
			{'name': '111111111', 'author_login': 'Test Login'},
		]

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 100,
				'type': 'label',
				'action': lambda player, values, instance:
				print(player, values, instance)
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'width': 50,
				'action': lambda player, values, instance:
				print(player, values, instance)
			},
		]

	async def get_actions(self):
		return [
			{
				'name': 'Delete',
				'action': self.action_delete,
				'style': 'Icons64x64_1',
				'substyle': 'Close'
			}
		]

	async def action_delete(self, player, values, instance, **kwargs):
		print('Delete value: {}'.format(instance))



class SampleListView(ListView):
	model = Map
	query = Map.select()
	title = 'Map List Testing'
	icon_style = 'Icons64x64_1'
	icon_substyle = 'Browser'

	async def get_fields(self):
		return [
			{
				'name': 'Name',
				'index': 'name',
				'sorting': True,
				'searching': True,
				'width': 100,
				'type': 'label',
				'action': lambda player, values, instance:
				print(player, values, instance)
			},
			{
				'name': 'Author',
				'index': 'author_login',
				'sorting': True,
				'searching': True,
				'renderer': lambda row, field:
				row.author_nickname if row.author_nickname and len(row.author_nickname) > 0 else row.author_login,
				'width': 50,
				'action': lambda player, values, instance:
				print(player, values, instance)
			},
		]

	async def get_actions(self):
		return [
			{
				'name': 'Delete',
				'action': self.action_delete,
				'style': 'Icons64x64_1',
				'substyle': 'Close'
			}
		]

	async def action_delete(self, player, values, instance, **kwargs):
		print('Delete value: {}'.format(instance))
