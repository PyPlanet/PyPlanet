import asyncio
from inspect import iscoroutinefunction

from pyplanet.contrib.command.params import ParameterParser


class Command:
	"""
	The command instance describes the command itself, the target to fire and all other related information, like
	admin command or aliases.

	Some examples of some commands:

	.. code-block:: python

		# Admin command with permission on it.
		Command(command='reboot', target=self.reboot_pool, perms='admin:reboot', admin=True)

		# Normal user command with optional argument.
		Command(command='list', target=self.show_map_list)\
			.add_param(name='search', required=False)

	"""

	def __init__(
		self, command, target, aliases=None, admin=False, namespace=None, parser=None, perms=None, description=None
	):
		"""
		Initiate a command.

		:param command: Command text (prefix without parameters).
		:param target: Target method to fire.
		:param aliases: Alias(ses) for the command.
		:param admin: Register command in admin context.
		:param namespace: Custom namespace, this can be used to create commands like '/prog start' and '/prog end'
						  where 'prog' is the namespace.
		:param perms: Required parameters, default everyone is allowed.
		:param parser: Custom parser.
		:param description: Description of the command.
		:type command: str
		:type target: any
		:type aliases: str[]
		:type admin: bool
		:type namespace: str, str[]
		:type perms: list,str
		:type parser: any
		:type description: str
		"""
		self.command = command
		self.target = target
		self.aliases = aliases or list()
		self.admin = admin
		self.namespace = namespace
		if isinstance(perms, str):
			perms = [perms]
		self.perms = perms
		self.parser = parser or \
					  ParameterParser('{} {}'.format(self.namespace, self.command) if self.namespace else self.command)
		self.description = description

	def match(self, raw):
		"""
		Try to match the command with the given input in array style (splitted by spaces).

		:param raw: Raw input, split by spaces.
		:type raw: list
		:return: Boolean if command matches.
		"""
		input = raw[:]

		if len(input) == 0:
			return False

		if self.admin:
			if input[0][0:1] == '/':
				input[0] = input[0][1:]
			elif input[0] == 'admin':
				input.pop(0)
			else:
				return False

		# Make sure namespace is always an array if provided.
		if self.namespace and not isinstance(self.namespace, (list, tuple)):
			self.namespace = [self.namespace]

		# Check against namespace.
		if len(input) > 0 and self.namespace and any(input[0] == n for n in self.namespace):
			input.pop(0)
		elif self.namespace:
			return False

		if not len(input):
			return False

		command = input.pop(0)
		if self.command == command or command in self.aliases:
			return True
		return False

	def get_params(self, input):
		"""
		Get params in array from input in array.

		:param input: Array of raw input.
		:type input: list
		:return: Array of parameters, stripped of the command name and namespace, if defined.
		:rtype: list
		"""
		if self.admin:
			if input[0][0:1] == '/':
				input[0] = input[0][1:]
			elif input[0] == 'admin':
				input.pop(0)
		if self.namespace:
			input.pop(0)
		input.pop(0)
		return input

	def add_param(
		self, name: str,
		nargs=1,
		type=str,
		default=None,
		required: bool=True,
		help: str=None,
		dest: str=None,
	):
		"""
		Add positional parameter.

		:param name: Name of parameter, will be used to store result into!
		:param nargs: Number of arguments, use integer or '*' for multiple or infinite.
		:param type: Type of value, keep str to match all types. Use any other to try to parse to the type.
		:param default: Default value when no value is given.
		:param required: Set the parameter required state, defaults to true.
		:param help: Help text to display when parameter is invalid or not given and required.
		:param dest: Destination to save into namespace result (defaults to name).
		:return: parser instance
		:rtype: pyplanet.contrib.command.command.Command
		"""
		self.parser.add_param(
			name=name, nargs=nargs, type=type, default=default, required=required, help=help, dest=dest
		)
		return self

	async def handle(self, instance, player, argv):
		"""
		Handle command parsing and execution.

		:param player: Player object.
		:param argv: Arguments in array
		:type player: pyplanet.apps.core.maniaplanet.models.player.Player
		"""
		# Check permissions.
		if self.perms and len(self.perms) > 0:
			# All the given perms need to be matching!
			is_allowed = await asyncio.gather(*[
				instance.permission_manager.has_permission(player, perm) for perm in self.perms
			])
			if not all(allowed is True for allowed in is_allowed):
				await instance.chat(
					'$z$sYou are not authorized to use this command!',
					player.login
				)
				return

		# Strip off the namespace and command.
		paramv = self.get_params(argv)

		# Parse, validate and show errors if any.
		self.parser.parse(paramv)
		if not self.parser.is_valid():
			await instance.gbx.multicall(
				instance.chat('$z$sCommand operation got invalid arguments: {}'.format(', '.join(self.parser.errors)), player),
				instance.chat('$z$s >> {}'.format(self.usage_text), player),
			)
			return

		# We are through. Call our target!
		if iscoroutinefunction(self.target):
			return await self.target(player=player, data=self.parser.data, raw=argv, command=self)
		return self.target(player=player, data=self.parser.data, raw=argv, command=self)

	@property
	def usage_text(self):
		"""
		The usage text line for the command.
		"""
		text = 'Usage: /{}{}{}'.format(
			'/' if self.admin else '',
			self.namespace if self.namespace else '',
			self.command
		)
		for param in self.parser.params:
			text += ' {}{}:{}{}'.format(
				'[' if not param['required'] else '',
				param['name'],
				getattr(param['type'], '__name__', 'any'),
				']' if not param['required'] else '',
			)

		return text

	def __str__(self):
		# Make sure namespace is always an array if provided.
		if self.namespace and not isinstance(self.namespace, (list, tuple)):
			self.namespace = [self.namespace]

		return '/{}{}{}'.format(
			'/' if self.admin else '',
			'|'.join(self.namespace) if self.namespace and isinstance(self.namespace, (list, tuple)) else self.command,
			' ' + self.command if self.namespace else '',
		)
