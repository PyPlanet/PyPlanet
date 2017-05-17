from xmlrpc.client import Fault


class DedimaniaException(Exception):
	"""
	General exception for dedimania.
	"""
	pass


class DedimaniaTransportException(DedimaniaException):
	"""
	Transport, decode or encode issue.
	"""
	pass


class DedimaniaNotSupportedException(DedimaniaException):
	"""
	Map or mode is not supported by Dedimania.
	"""
	pass


class DedimaniaInvalidCredentials(DedimaniaException):
	"""
	Invalid code or player.
	"""
	pass


class DedimaniaFault(DedimaniaException, Fault):
	"""
	Dedimania XMLRPC Fault.
	"""
	pass
