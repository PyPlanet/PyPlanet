import collections

from xmlrpc.client import Fault

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.contrib.chat.exceptions import ChatException
from pyplanet.core.gbx.query import Query


class ChatQuery(Query):
	"""
	The chat query is the chat message building class in PyPlanet.

	Please get a new instance from the chat manager with ``instance.chat.prepare()`` and chain your methods from there.
	"""

	def __init__(self, chat_manager, message=None, logins=None, auto_prefix=True):
		"""
		Build a chat query with this class, but please use it with the chat contrib ``prepare`` method.

		:param chat_manager: Chat manager instance.
		:param message: Optional predefined message.
		:param logins: Optional list of logins, or None (default) for global.
		:param auto_prefix: Optional: Automatically add prefix if it's public or private to the message.
		:type chat_manager: pyplanet.contrib.chat.manager.ChatManager
		"""
		self.chat_manager = chat_manager
		self.instance = chat_manager.instance

		self.auto_prefix = auto_prefix

		self._message = message or ''
		self._logins = logins

		query = self.gbx_query
		super().__init__(self.instance.gbx, query.method, *query.args)

	@property
	def method(self):
		return self.gbx_query.method

	@method.setter
	def method(self, _):
		pass

	@property
	def args(self):
		return self.gbx_query.args

	@args.setter
	def args(self, _):
		pass

	def to_players(self, *players):
		"""
		Set the destination of the chat message.

		:param players: Player instance(s) or player login string(s). Can be a list, or a single entry.
		:return: Self reference.
		:rtype: pyplanet.contrib.chat.query.ChatQuery
		"""
		# Unpack list in unpacked list if given.
		if len(players) == 1 and isinstance(players[0], collections.Iterable):
			players = players[0]

		# Replace logins.
		if isinstance(players, Player):
			self._logins = set()
			self._logins.add(players.login)
		elif isinstance(players, str):
			self._logins = set()
			self._logins.add(players)
		elif isinstance(players, collections.Iterable) and isinstance(players, collections.Sized):
			self._logins = set()
			self.add_to(players)
		return self

	def add_to(self, *players):
		"""
		Add new recipient to the to list.

		:param players: Player login string(s) or player instance(s).
		:return: Self reference.
		:rtype: pyplanet.contrib.chat.query.ChatQuery
		"""
		# Unpack list in unpacked list if given.
		if len(players) == 1 and isinstance(players[0], collections.Iterable):
			players = players[0]

		# Check if we already have login lists.
		if not isinstance(self._logins, set):
			self._logins = set()

		for obj in players:
			if isinstance(obj, Player):
				self._logins.add(obj.login)
			elif isinstance(obj, str):
				self._logins.add(obj)
		return self

	def to_all(self):
		"""
		Send message to all players on server (default).

		:return: Self reference.
		:rtype: pyplanet.contrib.chat.query.ChatQuery
		"""
		self._logins = None
		return self

	def message(self, message: str):
		"""
		Set the message payload.

		:param message: Message of the chat message.
		:return: Self reference.
		:rtype: pyplanet.contrib.chat.query.ChatQuery
		"""
		self._message = message
		return self

	def get_formatted_message(self):
		"""
		Get the formatted message. (will get the message string with prefix if applied).

		:return: String
		:rtype: str
		"""
		if not isinstance(self._message, str):
			raise ChatException('Chat message must be defined as a string! Use the .message() on your chat query!')

		message = ''

		# Add prefixes if public or private chat message.
		if self.auto_prefix:
			if isinstance(self._logins, set):
				message = '$z$s$fff» '
			else:
				message = '$z$s$fff»» '

		# Add the message payload.
		return message + self._message

	def prepare(self):
		"""
		Get a prepared gbx query for this chat message.

		:return: Prepared GBX query.
		:rtype: pyplanet.core.gbx.query.Query
		"""
		super().prepare()
		return self.gbx_query

	@property
	def gbx_query(self):
		"""
		Get a prepared gbx query for this chat message.

		:return: Prepared GBX query.
		:rtype: pyplanet.core.gbx.query.Query
		"""
		method = 'ChatSendServerMessage'
		args = list()
		args.append(self.get_formatted_message())

		if isinstance(self._logins, set):
			method = 'ChatSendServerMessageToLogin'
			args.append(','.join(self._logins))

		return self.instance.gbx(method, *args)

	async def execute(self):  # pragma: no cover
		"""
		Execute the chat message sending query. Please don't use this when you send multiple chat messages or actions!

		:return: Result of query.
		"""
		try:
			return await self.gbx_query.execute()
		except Fault as e:
			if 'Login unknown' in e.faultString:
				return True  # Ignore
			raise
