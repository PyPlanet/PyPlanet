import asynctest

from pyplanet.contrib.chat.exceptions import ChatException
from pyplanet.contrib.chat.query import ChatQuery
from pyplanet.core import Controller


class TestChat(asynctest.TestCase):
	async def test_simple(self):
		instance = Controller.prepare(name='default').instance
		chat = instance.chat.prepare()
		assert isinstance(chat, ChatQuery)

		chat.to_all().message('Test')
		assert len(chat.get_formatted_message()) > len('Test')  # Must include the prefix!!

	async def test_to_logins(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()
		await instance.db.initiate()

		from pyplanet.apps.core.maniaplanet.models import Player

		try:
			player1 = await Player.get(login='sample-1')
		except:
			player1 = await Player.create(login='sample-1', nickname='sample-1', level=Player.LEVEL_MASTER)

		try:
			player2 = await Player.get(login='sample-2')
		except:
			player2 = await Player.create(login='sample-2', nickname='sample-2', level=Player.LEVEL_PLAYER)

		# Try list.
		chat = instance.chat.prepare().to_players([player1, player2])
		assert 'sample-1' in chat._logins and 'sample-2' in chat._logins

		# Try unpacked list.
		chat = instance.chat.prepare().to_players(*[player1, player2])
		assert 'sample-1' in chat._logins and 'sample-2' in chat._logins

		# Try login list.
		chat = instance.chat.prepare().to_players([player1.login, player2.login])
		assert 'sample-1' in chat._logins and 'sample-2' in chat._logins

		# Try login unpacked list.
		chat = instance.chat.prepare().to_players(*[player1.login, player2.login])
		assert 'sample-1' in chat._logins and 'sample-2' in chat._logins

	async def test_query_conversion(self):
		instance = Controller.prepare(name='default').instance
		# MOCK:
		instance.gbx.gbx_methods = ['ChatSendServerMessageToLogin', 'ChatSendServerMessage']

		chat = instance.chat.prepare().to_players(['test-1', 'test-2']).message('Test')
		assert chat.gbx_query.method == 'ChatSendServerMessageToLogin'
		assert len(chat.gbx_query.args) == 2

		chat = instance.chat.prepare().message('Test')
		assert chat.gbx_query.method == 'ChatSendServerMessage'
		assert len(chat.gbx_query.args) == 1

		chat = instance.chat.prepare().to_all().message('Test')
		assert chat.gbx_query.method == 'ChatSendServerMessage'
		assert len(chat.gbx_query.args) == 1

	async def test_short_syntax(self):
		instance = Controller.prepare(name='default').instance
		# MOCK:
		instance.gbx.gbx_methods = ['ChatSendServerMessageToLogin', 'ChatSendServerMessage']

		prepared = instance.chat('Test')
		assert isinstance(prepared, ChatQuery)
