import argparse
from typing import Any


class ParameterParser:
	"""
	Parameter Parser.
	"""

	def __init__(self, prog=None):
		self.prog = prog
		self.params = list()
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument()

	def add_param(
		self, name: str,
		nargs=1,
		type: Any=str,
		default: Any=None,
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
		:rtype: pyplanet.contrib.command.ParameterParser
		"""
		self.params.append(dict(
			name=name, nargs=nargs, type=type, default=default, required=required, help=help, dest=dest
		))

	# TODO: Write logic for parsing
	# TODO: Write logic for validating
	# TODO: Write logic for parameter data receiving
