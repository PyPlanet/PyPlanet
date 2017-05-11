from argparse import Namespace

from pyplanet.contrib.command.exceptions import (
	ParamValidateException, ParamParseException, ParamException,
	NotValidated,
	InvalidParamException)


class ParameterParser:
	"""
	Parameter Parser.
	
	.. todo::
	
		Write introduction + examples.
		
	"""

	def __init__(self, prog=None):
		self.prog = prog
		self.params = list()

		self._errors = list()
		self.data = object()

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
		:rtype: pyplanet.contrib.command.ParameterParser
		"""
		self.params.append(dict(
			name=name, nargs=nargs, type=type, default=default, required=required, help=help, dest=dest
		))
		return self

	def parse_parameter(self, param, input, position):
		"""
		Validate and parse param value at input position.
		
		:param param: Param dict given.
		:param input: Full params input (without command or namespace!)
		:param position: Current seek position.
		:type param: dict
		:type input: list
		:type position: int
		:return: value.
		"""
		try:
			part = input[position]
		except IndexError:
			if param['required'] is False:
				return param['default']
			else:
				raise ParamValidateException('param \'{}\' is required'.format(param['name']))

		value = None
		# If we have multiple arguments of the same type, parse it internally.
		if isinstance(param['nargs'], int) and param['nargs'] > 1:
			# We need to clone to prevent infinite loop
			nparam = dict()
			nparam.update(param)
			nparam['nargs'] = 1

			value = []
			errors = []
			for i in range(1, param['nargs']):
				try:
					value.append(self.parse_parameter(nparam, input, position + i))
				except ParamException as e:
					errors.append(str(e))
			if len(errors) > 0:
				raise ParamParseException(', '.join(errors))

		# If we expect multiple (infinite) occurrences.
		elif isinstance(param['nargs'], str) and param['nargs'] == '*':
			# We need to clone to prevent infinite loop
			nparam = dict()
			nparam.update(param)
			nparam['nargs'] = 1

			if value:
				value = [value]
			else:
				value = []

			for i in range(0, len(input)):
				try:
					extra_value = self.parse_parameter(nparam, input, position + i)
					if extra_value is not None:
						value.append(extra_value)
				except ParamException:
					# We will stop here.
					break

		else:
			if param['type'] is int:
				try:
					value = int(part)
				except ValueError:
					raise ParamParseException('param \'{}\' must be an integer'.format(param['name']))
			elif param['type'] is str:
				value = part
			else:
				raise InvalidParamException('Type of parameter \'{}\' is not known.'.format(param['name']))

		return value

	def parse(self, argv):
		"""
		Parse arguments.
		
		:param argv: arguments.
		"""
		values = dict()

		self.data = None
		self._errors = list()

		for idx, param in enumerate(self.params):
			try:
				values[param['dest'] or param['name']] = self.parse_parameter(param, argv, idx)
			except ParamException as e:
				self._errors.append(str(e))

		self.data = Namespace(**values)

	def is_valid(self):
		"""
		Is data valid?
		
		:return: boolean
		"""
		if self.data is None:
			raise NotValidated('Parameters not yet parsed, call parse() first.')
		return len(self._errors) == 0

	@property
	def errors(self):
		"""
		Get errors.
		
		:return: array of strings.
		:rtype: list
		"""
		return self._errors
