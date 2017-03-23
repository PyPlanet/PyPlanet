
class _Game:
	"""
	The game class holds information about the game itself and the server. The names of the properties are all virtual
	and are cached so it can be as stable as possible, this way we can provide a read-only data structure and still
	maintain the same structure if any of the third party API changes.
	"""
	def __init__(self):
		pass

Game = _Game()
