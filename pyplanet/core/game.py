
class _Game:
	"""
	The game class holds information about the game itself and the server. The names of the properties are all virtual
	and are cached so it can be as stable as possible, this way we can provide a read-only data structure and still
	maintain the same structure if any of the third party API changes.
	"""
	_dedicated_build = None
	_dedicated_version = None
	_dedicated_api_version = None

	@property
	def dedicated_build(self):
		return self._dedicated_build

	@property
	def dedicated_version(self):
		return self._dedicated_version

	@property
	def dedicated_api_version(self):
		return self._dedicated_api_version

Game = _Game()
