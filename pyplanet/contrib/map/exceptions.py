

class MapException(Exception):
	"""Generic map exception by manager."""


class MapNotFound(MapException):
	"""Map not found"""


class MapIncompatible(MapException):
	"""The map you want to add/insert/upload is invalid and not suited for the current server config."""
