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


class DedimaniaFault(DedimaniaException, Fault):
	"""
	Dedimania XMLRPC Fault.
	"""
	pass
