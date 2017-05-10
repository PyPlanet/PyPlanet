
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
