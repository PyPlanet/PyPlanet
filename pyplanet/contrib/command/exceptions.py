

class ParamException(Exception):
	pass


class ParamParseException(ParamException):
	pass


class ParamValidateException(ParamException):
	pass


class NotValidated(Exception):
	"""
	Your parser hasn't been called with .parse() before, so no parsing took place!
	"""
	pass


class InvalidParamException(Exception):
	"""
	Invalid parameter arguments given!
	"""
