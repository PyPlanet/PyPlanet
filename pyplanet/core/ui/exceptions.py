

class UIException(Exception):
	"""
	Base exception for UI core component.
	"""
	pass


class ManialinkMemoryLeakException(UIException):
	"""
	Is thrown when a memory leak is detected in a view. Raised when a manialink responds to a view, but the view is 
	vanished for the specified player(s).
	"""
	pass


class UIPropertyDoesNotExist(UIException):
	"""
	Thrown when UI Property with element doesn't exist.
	"""
	pass
