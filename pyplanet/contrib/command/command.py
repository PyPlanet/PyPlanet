
from .params import ParameterParser


class Command:
	"""
	The command instance describes the command itself, the target to fire and all other related information, like
	admin command or aliases.
	"""
	def __init__(
		self, command, target, aliases=None, admin=False, parser=None
	):
		self.command = command
		self.target = target
		self.aliases = aliases
		self.admin = admin
		self.parser = parser or ParameterParser(self.command)

	def parse(self, args):
		pass

	def fire(self):
		pass
